---
schema_version: 1
id: openrouter-client
domain: 02-openrouter
status: draft
title: "TODO-01 -- OpenRouter Client"
depends_on: []
---

# TODO-01 -- OpenRouter Client

> **Goal:** `src/services/openrouter.ts` talks to OpenRouter over plain `fetch` with no SDK: one-shot chat completions, SSE streaming with cancellation, structured JSON output, the model catalogue, and the key status, each classifying every documented failure into a typed error, and each proven by an API contract test that replays committed fixtures of real OpenRouter responses. Nothing calls it yet: the callers move in D02 T02, so the Gemini path keeps working until the cutover.

> [!IMPORTANT]
> **Current state (verified 2026-09-27):** The only AI client is `src/services/gemini.ts` (441 lines) over `@google/genai` (`package.json` `"@google/genai": "^1.42.0"`, imported once, at `gemini.ts` line 13). It owns the retry loop (`MAX_RETRIES = 3`, `INITIAL_RETRY_DELAY_MS = 1000`, factor 2, jitter), the adaptive timeout (`calcTimeout`: 30 s plus 10 s per 5,000 prompt characters, capped at 90 s), and `classifyError`, whose `QUOTA_EXCEEDED` branch can never run because the 429 branch above it returns first. `withTimeout` rejects without aborting, so a timed-out request keeps running. There is no `src/services/openrouter.ts`, no fixtures folder, and no test that replays a recorded response: `src/services/gemini.test.ts` mocks the SDK's `generateContent` directly, and its retry tests wait on real timers. Jest runs in the `node` environment (`jest.config.js`), where Node 24 provides a global `fetch`, `ReadableStream`, and `AbortController`.
<!-- claim: absent src/services/openrouter.ts -->
<!-- claim: absent src/services/__fixtures__/openrouter -->
<!-- claim: count "from '@google/genai'" src/services/gemini.ts = 1 -->
<!-- claim: count "thinkingBudget" src/services/gemini.ts = 1 -->
<!-- claim: lines src/services/gemini.ts = 441 -->

## Inputs

- [`src/services/gemini.ts`](../../src/services/gemini.ts) -- the retry, timeout, and error-classification behavior §2 carries over, and the defects it does not (the unreachable `QUOTA_EXCEEDED` branch, the timeout that does not abort)
- [`src/services/gemini.test.ts`](../../src/services/gemini.test.ts) -- the cases §2's tests must keep covering (401, 403, empty response, network failure, retry on 429 and 5xx, exhausted retries)
- OpenRouter API reference, overview and chat completions (https://openrouter.ai/docs/api-reference/overview) -- the `POST /api/v1/chat/completions` request, the `Authorization: Bearer` header, the optional app-attribution headers (`HTTP-Referer`, and `X-OpenRouter-Title`, formerly `X-Title`), `finish_reason` values (`stop`, `length`, `content_filter`, `tool_calls`, `error`)
- OpenRouter errors (https://openrouter.ai/docs/errors) -- the `{ error: { code, message, metadata } }` body, the status list (400, 401, 402, 403 with moderation `metadata.reasons`, 408, 429, 502, 503), and the mid-stream error chunk with `finish_reason: "error"`
- OpenRouter streaming (https://openrouter.ai/docs/api-reference/streaming) -- SSE `data:` lines, `: OPENROUTER PROCESSING` comment lines, the `data: [DONE]` terminator, the usage chunk before it, and `AbortController` cancellation
- OpenRouter structured outputs (https://openrouter.ai/docs/structured-outputs) -- `response_format: { type: "json_schema", json_schema: { name, strict, schema } }` and `provider.require_parameters`
- OpenRouter models (https://openrouter.ai/docs/api-reference/models/get-models) -- `GET /api/v1/models`: `id`, `name`, `context_length`, `pricing.prompt`, `pricing.completion`, `architecture.input_modalities`, `architecture.output_modalities`, `supported_parameters`
- OpenRouter limits (https://openrouter.ai/docs/api-reference/limits) -- `GET /api/v1/key`: `label`, `usage`, `limit`, `limit_remaining`, `is_free_tier`
- -> XREF: D02 T02 §1 -- the facade that consumes `chat()`, `streamChat()`, and `chatJson()`; D02 T02 §4 consumes `listModels()` and D02 T02 §5 consumes `keyInfo()`
- -> XREF: D03 T03 §4 -- context-length handling reads `contextLength` from the catalogue §5 builds

## Outcome

- `src/services/openrouter.ts` exports `chat()`, `streamChat()`, `chatJson()`, `listModels()`, `keyInfo()`, and `OpenRouterError`, imports nothing from `src/features/`, and takes the API key as an argument, so the settings-to-client circular import cannot recur.
- Every documented status (400, 401, 402, 403, 408, 429, 502, 503), a network failure, a timeout, a user cancel, an empty completion, `finish_reason: "length"` with no content, and a mid-stream error each map to one `OpenRouterError` code with the right `retryable` flag, proven by a contract test per case.
- Committed fixtures under `src/services/__fixtures__/openrouter/` replay through the client in `npx jest src/services/openrouter.test.ts` with `fetch` mocked and no network.
- A timeout or a cancel aborts the underlying `fetch` (the request is gone, not merely ignored).

**Adjacency:** all=not-applicable (a service module with no surface, no stored user records, and no user action of its own; its consumers in D02 T02 carry the settings, notifications, and permissions obligations)

## Implementation Order

| Order | Section | Deliverable                                | Depends On | Status |
| :---: | :-----: | ------------------------------------------ | ---------- | :----: |
|   1   |   §1    | Record the OpenRouter contract fixtures    | --         |  [ ]   |
|   2   |   §2    | Chat completions over fetch                | §1         |  [ ]   |
|   3   |   §3    | Streaming over SSE                         | §2         |  [ ]   |
|   4   |   §4    | Structured JSON output                     | §2         |  [ ]   |
|   5   |   §5    | The models catalogue                       | §2         |  [ ]   |
|   6   |   §6    | Key status                                 | §2         |  [ ]   |

---

## 1. Record the OpenRouter Contract Fixtures

The API contract proof (`todo/README.md`) replays real OpenRouter responses, so the fixtures come first and come from the real endpoint. Each fixture is recorded by one script, redacted, and committed with the date and the command that produced it. Cases the endpoint cannot be made to produce on demand (a 402 on a funded key, a 429, a mid-stream provider failure) are written by hand from the documented shape, and are marked synthetic with the documentation URL beside them, so nobody mistakes them for a recording.

**Needs:** OpenRouter API key (live test)

- [ ] Write `scripts/record-openrouter-fixtures.ts` (run with `npx ts-node`), reading `OPENROUTER_API_KEY` from `.env` through `dotenv`, never printing it. Done when: running it without the variable exits `1` with "OPENROUTER_API_KEY is not set" and prints no request.
- [ ] Record, into `src/services/__fixtures__/openrouter/`: `chat-completion.json` (a one-sentence reply, `stream: false`), `chat-stream.sse` (the same prompt with `stream: true`, the raw body byte for byte, including any `: OPENROUTER PROCESSING` comment lines, the usage chunk, and `data: [DONE]`), `chat-json-schema.json` (a `response_format` json_schema request against a model whose `supported_parameters` include `structured_outputs`), `error-400.json` (an invalid `temperature: 5`), `error-401.json` (a deliberately wrong key), `models.json` (`GET /api/v1/models`, trimmed to 10 models including one image-output model and one with `structured_outputs`), and `key.json` (`GET /api/v1/key`). Each file stores `{ "status": <http status>, "headers": {<content-type, retry-after if any>}, "body": ... }` except `.sse`, whose status and headers go in `chat-stream.meta.json`. Done when: the eight files exist and parse.
- [ ] Redact: the script replaces the key, the `label` value in `key.json`, and any `id` that could identify the account (`gen-...` generation ids are kept, they are per-request) with fixed placeholders, and the prompts are fixed sentences with no personal data. Done when: `grep -rn "sk-or-" src/services/__fixtures__/openrouter` prints nothing.
- [ ] Hand-write `error-402.json`, `error-403-moderation.json` (with `metadata.reasons`, `flagged_input`, `provider_name`, `model_slug`), `error-429.json` (with a `retry-after` header), `error-502.json`, `error-503.json`, and `chat-stream-midstream-error.sse` (a few content chunks, then a chunk with a top-level `error` and `finish_reason: "error"`) from https://openrouter.ai/docs/errors, each carrying `"synthetic": true` and `"source": "<doc URL>"`. Done when: every synthetic file has both fields.
- [ ] Write `src/services/__fixtures__/openrouter/README.md` listing every fixture, whether it is recorded or synthetic, the recording date, the model id used, and the command `npx ts-node scripts/record-openrouter-fixtures.ts`. Done when: the README lists every file in the folder (checked by a loop over `ls`).
- [ ] Commit: `"openrouter: record the API contract fixtures"`

**Test checkpoint:** `npx ts-node scripts/record-openrouter-fixtures.ts` with a valid key rewrites the recorded fixtures and `git diff --stat` shows only response-content changes (ids, timestamps, text), never a shape change; without the key it exits `1`; `grep -rn "sk-or-" src/services/__fixtures__/openrouter` prints nothing; a short Node check parses every `.json` fixture and asserts `chat-stream.sse` ends with `data: [DONE]`. Cheaper substitute that fails: fixtures typed by hand from the documentation for every case, which cannot show that the real stream carries comment lines or a usage chunk, and fails the `[DONE]` and comment-line assertions against a real recording.

## 2. Chat Completions Over Fetch

The one-shot call every other section builds on: request shape, headers, timeout that actually aborts, retry with backoff, and error classification from OpenRouter's error body instead of from message text. The retry and timeout constants carry over from `gemini.ts` so behavior does not drift at the cutover.

- [ ] Create `src/services/openrouter.ts` with `OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"`, the request and response types (`ChatMessage`, `ChatRequest` with `model`, `messages`, `temperature`, `max_tokens`, `top_p`, `stream`, `response_format`, `provider`, `reasoning`, `usage`; `ChatResponse` with `choices[].message.content`, `choices[].finish_reason`, `usage`), and `chat(request, { apiKey, signal, timeoutMs })`. Done when: `npx tsc --noEmit` exits `0` for the file. Source: https://openrouter.ai/docs/api-reference/overview.
- [ ] Send `Authorization: Bearer <apiKey>`, `Content-Type: application/json`, `HTTP-Referer: https://rizonesoft.github.io/Gemail/`, and the app-title header the reference names at build time (`X-OpenRouter-Title: Gemail`; `X-Title` is its older name). Done when: a test named `sends auth and attribution headers` asserts all four on the mocked `fetch` call.
- [ ] Implement the timeout with an internal `AbortController` linked to the caller's `signal`, using `calcTimeout()` moved from `gemini.ts`; a timeout aborts the fetch and raises `TIMEOUT`, a caller abort raises `CANCELLED`. Done when: tests named `timeout aborts the fetch` (the mocked fetch observes `signal.aborted === true`) and `caller abort is CANCELLED, not retried` pass under `jest.useFakeTimers()`. Cheaper substitute: a `Promise.race` timeout like `withTimeout`, which leaves the fetch running and fails the `signal.aborted` assertion.
- [ ] Implement `OpenRouterError` (`code`, `status`, `retryable`, `metadata`, `retryAfterMs`) and `classify(status, body)` from the error body: 400 `BAD_REQUEST` (or `CONTEXT_TOO_LONG` when the message names the context length), 401 `INVALID_API_KEY`, 402 `INSUFFICIENT_CREDITS`, 403 `MODERATION` (keeping `metadata.reasons`), 408 `TIMEOUT` retryable, 429 `RATE_LIMITED` retryable (honoring `retry-after`), 502 `MODEL_UNAVAILABLE` retryable, 503 `NO_PROVIDER` retryable, a `TypeError` from `fetch` `NETWORK` retryable, anything else `UNKNOWN`. Done when: one test per code replays the matching `error-*.json` fixture and asserts code and `retryable`. Source: https://openrouter.ai/docs/errors.
- [ ] Classify successful responses too: empty `content` with `finish_reason: "length"` raises `TRUNCATED`, `finish_reason: "content_filter"` raises `CONTENT_FILTERED`, other empty content raises `EMPTY_RESPONSE`. Done when: three tests built from `chat-completion.json` with the field edited in the test pass.
- [ ] Port `retryWithBackoff()` (3 retries, 1 s start, factor 2, 30 percent jitter), retrying only `retryable` errors and waiting `retryAfterMs` when a 429 carries it. Done when: tests named `retries 429 then succeeds`, `honors retry-after`, and `gives up after 3 retries` pass with fake timers in under one second of real time.
- [ ] Commit: `"openrouter: chat completions over fetch with typed errors"`

**Test checkpoint:** `npx jest src/services/openrouter.test.ts` passes every named test above with `global.fetch` mocked to replay `chat-completion.json` and the `error-*.json` fixtures, and no test touches the network (a guard in the test file fails any unmocked `fetch`); the replayed completion returns the fixture's exact content string. Cheaper substitute that fails: classifying by regex on `error.message` as `gemini.ts` does, which misreads the 402 fixture (its message names no status word the regexes match) and fails the per-code tests.

## 3. Streaming Over SSE

Streaming lets the result card show text as it arrives and lets the user stop a long reply (D03 T02 §4 builds the surface). The parser must survive real network chunking: a chunk boundary can fall anywhere, including inside a `data:` line or inside a multi-byte character.

- [ ] Implement `streamChat(request, { apiKey, signal, timeoutMs })` as an `AsyncGenerator<StreamEvent>` yielding `{ type: "delta", text }` per content delta and one final `{ type: "done", finishReason, usage }`; it sends `stream: true` and reads `response.body` through a `TextDecoder` in streaming mode. Done when: replaying `chat-stream.sse` yields deltas whose concatenation equals the recorded text and a `done` event carrying the recorded `usage`. Source: https://openrouter.ai/docs/api-reference/streaming.
- [ ] Buffer across chunks and split on line boundaries only; ignore lines starting with `:` (for example `: OPENROUTER PROCESSING`) and blank lines; stop at `data: [DONE]`. Done when: a test named `survives every chunk boundary` replays `chat-stream.sse` split at every byte offset (one run per offset) and gets the same text each time. Cheaper substitute: `chunk.split("\n")` per chunk, which fails at the offsets that cut a line in two.
- [ ] Surface a mid-stream error: a chunk with a top-level `error` and `finish_reason: "error"` ends the generator by throwing an `OpenRouterError` classified from `error.code`, after the deltas already yielded. Done when: replaying `chat-stream-midstream-error.sse` yields the content deltas, then throws, and the test asserts both.
- [ ] Apply the timeout to silence, not to total length: the stream fails with `TIMEOUT` when no byte arrives for `timeoutMs` (comment lines count as bytes), and a caller abort ends it with `CANCELLED` and cancels the reader. Done when: tests named `idle timeout aborts` and `abort cancels the reader` pass with fake timers.
- [ ] Pre-stream errors (a non-200 status before any body) go through the §2 classifier and the §2 retry; a stream that has yielded any delta is never retried. Done when: a test replaying `error-429.json` then `chat-stream.sse` succeeds, and a test with a mid-stream failure asserts exactly one `fetch` call.
- [ ] Commit: `"openrouter: SSE streaming with cancellation and mid-stream errors"`

**Test checkpoint:** `npx jest src/services/openrouter.stream.test.ts` passes the named tests, including the every-offset replay of the recorded stream and the mid-stream error replay; the recorded stream's concatenated text equals the `chat-completion.json` content where both were recorded from the same prompt at temperature 0, or the test compares against the text stored in `chat-stream.meta.json`. Cheaper substitute that fails: buffering the whole body with `response.text()` and parsing at the end, which yields no event before the stream ends and fails the test that asserts the first delta arrives before the last chunk is fed.

## 4. Structured JSON Output

Email scoring, action extraction, and later the thread timeline need JSON the code can trust. OpenRouter passes `response_format` json_schema to models that support it, and `provider.require_parameters: true` keeps the request away from providers that would ignore it. Models without support still get a usable result through a prompt instruction and a tolerant parser, validated against the same schema.

- [ ] Implement `chatJson<T>(request, { schema, name, apiKey, signal, supportsStructuredOutputs })`: when `supportsStructuredOutputs` is true, send `response_format: { type: "json_schema", json_schema: { name, strict: true, schema } }` and `provider: { require_parameters: true }` (merged with any caller `provider` fields); otherwise append one system message asking for JSON matching the schema. Done when: tests assert both request bodies on the mocked `fetch`. Source: https://openrouter.ai/docs/structured-outputs.
- [ ] Parse tolerantly: strip a Markdown code fence, then `JSON.parse`, then fall back to the first balanced `{...}` or `[...]` span. Done when: tests for a fenced reply, a reply with prose before the object, and plain JSON all return the object; a reply with no JSON raises `INVALID_JSON`.
- [ ] Validate the parsed value with `validateJson(value, schema)`, a small in-repo validator for the subset Gemail's schemas use (`type` object, array, string, number, integer, boolean; `properties`; `required`; `items`; `enum`; `minimum`; `maximum`), returning the first failing path. Done when: a test named `rejects a missing required field` names the path, and `chat-json-schema.json` validates clean. Cheaper substitute: casting `JSON.parse` output to `T`, which lets a reply missing `clarity` through and fails that test.
- [ ] Record in the section's commit body why no JSON-schema dependency is added (`AGENTS.md`: a dependency is a decision; the subset above is under 100 lines and fully tested). Done when: the reason is in the commit body.
- [ ] Commit: `"openrouter: structured JSON output with a validated fallback"`

**Test checkpoint:** `npx jest src/services/openrouter.json.test.ts` passes, including the replay of the recorded `chat-json-schema.json` through `chatJson()` returning an object that satisfies its schema, and the fallback path returning the same object from a fenced reply built from that fixture's content. Cheaper substitute that fails: always sending `response_format` without `require_parameters`, which the request-body test catches because the `provider` field is missing.

## 5. The Models Catalogue

The model picker (D02 T02 §4), the default-model choice (D02 T02 §3), structured-output support (§4), and context-length handling (D03 T03 §4) all read one catalogue. The full `/api/v1/models` response is large, so the client keeps only the fields Gemail uses and caches them.

- [ ] Implement `listModels({ apiKey, signal, storage, now })` returning `ModelInfo[]` with `id`, `name`, `contextLength`, `promptPrice`, `completionPrice` (USD per token, parsed from the string fields), `inputModalities`, `supportsStructuredOutputs` (`supported_parameters` includes `structured_outputs` or `response_format`), and `supportsReasoning` (`supported_parameters` includes `reasoning`), keeping only models whose `architecture.output_modalities` include `text`. Done when: replaying `models.json` returns the recorded text models and drops the image-output one. Source: https://openrouter.ai/docs/api-reference/models/get-models.
- [ ] Send the key when one is given (the reference lists the endpoint as authenticated) and work without it if the endpoint answers anonymously. Done when: tests for both request shapes pass.
- [ ] Cache the trimmed list in the injected `storage` (the browser's `localStorage` in production) under `gemail_models_cache` as `{ fetchedAt, models }` for 24 hours; serve a fresh cache without a request, refresh a stale one, and fall back to a stale cache when the refresh fails. Done when: tests named `serves a fresh cache without fetch`, `refreshes a stale cache`, and `falls back to a stale cache offline` pass with an injected clock.
- [ ] Measure the cached size for the full live catalogue once (with the §1 key) and record it in the commit body; fail the write gracefully (keep the in-memory list) when `setItem` throws a quota error. Done when: the size is recorded and a test with a throwing `storage.setItem` still returns the models.
- [ ] Commit: `"openrouter: the models catalogue with a 24-hour cache"`

**Test checkpoint:** `npx jest src/services/openrouter.models.test.ts` passes the named tests against `models.json`; the recorded structured-output model reports `supportsStructuredOutputs: true` and the image model is absent. Cheaper substitute that fails: caching the raw response, which the size-record item exposes and which returns the image-output model, failing the filter test.

## 6. Key Status

Test Connection (D02 T02 §5) and, later, the credit display need to know whether a key is valid and how much it can still spend, without spending anything. `GET /api/v1/key` answers both.

- [ ] Implement `keyInfo(apiKey, { signal })` returning `{ label, usage, limit, limitRemaining, isFreeTier }` from `GET /api/v1/key`, reading the fields under the response's `data` object when present. Done when: replaying `key.json` returns the recorded values with `limit: null` preserved as "no limit". Source: https://openrouter.ai/docs/api-reference/limits.
- [ ] Classify failures through the §2 classifier: a wrong key replays `error-401.json` and raises `INVALID_API_KEY`, not retried. Done when: the test asserts one `fetch` call and the code.
- [ ] Commit: `"openrouter: key status from the key endpoint"`

**Test checkpoint:** `npx jest src/services/openrouter.key.test.ts` passes: `key.json` replays to the typed object and `error-401.json` to `INVALID_API_KEY` with a single request. Cheaper substitute that fails: a one-token chat completion as the key check, which spends credit, cannot report the limit, and fails the `limitRemaining` assertion.

## Verification

- [ ] `pwsh scripts/check-all.ps1` -- exits 0: production build, typecheck, lint, tests, manifest, TODO gates green
- [ ] `npx jest --ci` exits 0 with the five `src/services/openrouter*.test.ts` files reporting and no network access (the unmocked-fetch guard never fires)
- [ ] Every fixture in `src/services/__fixtures__/openrouter/README.md` is replayed by at least one test (`grep` each fixture name across the test files)
