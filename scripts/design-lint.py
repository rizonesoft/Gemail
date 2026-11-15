#!/usr/bin/env python3
"""design-lint -- hold the plan and the code to the imported Gemail design.

Stdlib only, like the rest of scripts/, so the commit hook and CI run it with no
install step. Checks (docs/design/README.md is the prose version):

  FATAL, never baselined
    tokens          docs/design/tokens.json parses; light and dark carry the same
                    color keys; every color is #rrggbb.
    icons           assets/icons/manifest.json matches assets/icons/src/ (every
                    source recorded with its current sha256) and every output
                    (PNGs, src/ui/icons.ts) exists with its recorded sha256. A
                    changed source without `node tools/design/icons.mjs` fails.
    mockup          docs/design/mockup/ matches mockup/source.json (the pinned
                    artifact version and sha256 per file); every artboard in
                    canvas.json exists; every artboard has a render whose
                    recorded board sha256 is the current board's.
    mockup-tokens   every #rrggbb in the pane artboards (outside <svg>) is a token.
    todo            every `**Design:**` line in todo/ cites docs/design/mockup.md#<anchor>,
                    and every mockup.md anchor it cites exists.

  Ratcheted by docs/design/.lint-baseline.json (counts per file; may only shrink)
    color-literal   a hex, rgb(), or hsl() color in src/ outside the generated token file
    inline-svg      an <svg> in src/ outside the generated icon registry
    font-family     a font-family not using a token variable, Poppins, or Google Fonts
    legacy-icon     a manifest or src/ reference to the pre-2.0 PNGs (tool-icons/, assets/icon-NN.png)

Usage:
  python scripts/design-lint.py                    run every check (exit 1 on any failure)
  python scripts/design-lint.py --update-baseline  rewrite the baseline to current counts (refuses growth)
  python scripts/design-lint.py --relock-mockup VERSION
                                                   pin docs/design/mockup/ to an artifact version (design-sync skill)
  python scripts/design-lint.py --self-test        the script's own suite
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTIFACT_URL = "https://claude.ai/artifact/Vc5xq9U5iRvq1AiZ1gm5YD"
# The boards that draw the task pane. Main.dc.html is the overview (rationale, token swatches) and Icons.dc.html
# the icon sheet: neither is a pane surface, and the icon sheet carries the ribbon icons' own colors. States.dc.html
# (interaction states and the 16 px icon redraws) carries those icon colors too, so it is not listed either.
PANE_BOARDS = ("Reply.dc.html", "Settings.dc.html", "Improve.dc.html")
HEX = re.compile(r"^#[0-9a-f]{6}$")
RATCHET_RULES = ("color-literal", "inline-svg", "font-family", "legacy-icon")
# Generated files that are allowed to hold what the ratchet rules count.
GENERATED = {"src/ui/icons.ts", "src/styles/tokens.css"}
COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])|\b(?:rgba?|hsla?)\(")
FONT_RE = re.compile(r"font-family\s*:\s*([^;\"'}]+)|fontFamily\s*=|fonts\.googleapis\.com|fonts\.gstatic\.com|\bPoppins\b")
SVG_RE = re.compile(r"<svg\b")
LEGACY_ICON_RE = re.compile(r"tool-icons/|assets/icon-\d+\.png")
DESIGN_LINE_RE = re.compile(r"^\*\*Design:\*\*\s*(?P<body>.+)$")
MOCKUP_REF_RE = re.compile(r"docs/design/mockup\.md#([a-z0-9_-]+)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def sha256(path: Path) -> str:
    """Content hash that survives line-ending conversion: a Windows checkout
    (core.autocrlf) holds CRLF where the index and CI hold LF, so text files
    are hashed with CRLF folded to LF. Binary files (PNG) are hashed raw."""
    data = path.read_bytes()
    if path.suffix.lower() != ".png":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


# ------------------------------------------------------------------ tokens

def load_tokens(root: Path) -> tuple[dict, list[str]]:
    f = root / "docs/design/tokens.json"
    try:
        t = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, [f"tokens: {rel(root, f) if f.exists() else 'docs/design/tokens.json'} unreadable: {e}"]
    out = []
    colors = t.get("color", {})
    light, dark = colors.get("light", {}), colors.get("dark", {})
    if not light or not dark:
        out.append("tokens: color.light and color.dark are both required")
    if set(light) != set(dark):
        out.append(f"tokens: light and dark keys differ: {sorted(set(light) ^ set(dark))}")
    for theme, table in (("light", light), ("dark", dark)):
        for k, v in table.items():
            if not isinstance(v, str) or not HEX.match(v.lower()):
                out.append(f"tokens: color.{theme}.{k} = {v!r} is not #rrggbb")
    return t, out


def token_colors(tokens: dict) -> set[str]:
    return {v.lower() for th in ("light", "dark") for v in tokens.get("color", {}).get(th, {}).values()}


# ------------------------------------------------------------------ icons

def check_icons(root: Path) -> list[str]:
    out = []
    mf = root / "assets/icons/manifest.json"
    src = root / "assets/icons/src"
    if not src.is_dir():
        return ["icons: assets/icons/src/ is missing"]
    if not mf.is_file():
        return ["icons: assets/icons/manifest.json is missing; run `node tools/design/icons.mjs`"]
    m = json.loads(mf.read_text(encoding="utf-8"))
    actual = {rel(root, p): sha256(p) for p in sorted(src.rglob("*.svg"))}
    recorded = m.get("sources", {})
    for p, h in actual.items():
        if p not in recorded:
            out.append(f"icons: {p} is new since the last build; run `node tools/design/icons.mjs`")
        elif recorded[p] != h:
            out.append(f"icons: {p} changed since the last build; run `node tools/design/icons.mjs`")
    for p in recorded:
        if p not in actual:
            out.append(f"icons: {p} was removed since the last build; run `node tools/design/icons.mjs`")
    for p, h in m.get("outputs", {}).items():
        f = root / p
        if not f.is_file():
            out.append(f"icons: {p} is missing; run `node tools/design/icons.mjs`")
        elif sha256(f) != h:
            out.append(f"icons: {p} was edited by hand or is stale; run `node tools/design/icons.mjs`")
    if "src/ui/icons.ts" not in m.get("outputs", {}):
        out.append("icons: the manifest does not record src/ui/icons.ts")
    return out


# ------------------------------------------------------------------ mockup

def check_mockup(root: Path, tokens: dict) -> list[str]:
    out = []
    d = root / "docs/design/mockup"
    lock = d / "source.json"
    if not lock.is_file():
        return ["mockup: docs/design/mockup/source.json is missing; pin it with --relock-mockup <version>"]
    pinned = json.loads(lock.read_text(encoding="utf-8"))
    files = pinned.get("files", {})
    present = {p.name for p in d.iterdir() if p.is_file() and (p.suffix == ".json" and p.name != "source.json" or p.name.endswith(".dc.html"))}
    for name in sorted(present | set(files)):
        f = d / name
        if name not in files:
            out.append(f"mockup: {name} is not pinned in source.json; import through the design-sync skill")
        elif not f.is_file():
            out.append(f"mockup: {name} is pinned but missing")
        elif sha256(f) != files[name]:
            out.append(f"mockup: {name} differs from the pinned artifact version {pinned.get('version')}; "
                       "change the design in the artifact and re-import with the design-sync skill")
    canvas_f = d / "canvas.json"
    if canvas_f.is_file():
        canvas = json.loads(canvas_f.read_text(encoding="utf-8"))
        for board in canvas.get("order", []):
            if not (d / board).is_file():
                out.append(f"mockup: canvas.json lists {board}, which is missing")
        renders = d / "renders/manifest.json"
        rm = json.loads(renders.read_text(encoding="utf-8")) if renders.is_file() else {}
        for board in canvas.get("order", []):
            mine = {k: v for k, v in rm.items() if v.get("board") == board}
            if not mine:
                out.append(f"mockup: {board} has no render; run `node tools/design/render-mockup.mjs`")
            for png, v in mine.items():
                f = d / "renders" / png
                if not f.is_file():
                    out.append(f"mockup: renders/{png} is missing; run `node tools/design/render-mockup.mjs`")
                elif (d / board).is_file() and v.get("boardSha256") != sha256(d / board):
                    out.append(f"mockup: renders/{png} was made from an older {board}; run `node tools/design/render-mockup.mjs`")
                elif v.get("pngSha256") != sha256(f):
                    out.append(f"mockup: renders/{png} was edited by hand; run `node tools/design/render-mockup.mjs`")
    # every color the pane artboards use is a token
    colors = token_colors(tokens)
    for board in PANE_BOARDS:
        f = d / board
        if not f.is_file():
            continue
        text = re.sub(r"<svg[\s\S]*?</svg>", "", f.read_text(encoding="utf-8"))
        for c in sorted({c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", text)}):
            if c not in colors:
                out.append(f"mockup-tokens: {board} uses {c}, which is not in docs/design/tokens.json")
    return out


def relock_mockup(root: Path, version: str) -> Path:
    d = root / "docs/design/mockup"
    files = {p.name: sha256(p) for p in sorted(d.iterdir())
             if p.is_file() and p.name != "source.json" and (p.suffix == ".json" or p.name.endswith(".dc.html"))}
    lock = d / "source.json"
    lock.write_text(json.dumps({"artifact": ARTIFACT_URL, "version": version, "files": files}, indent=2) + "\n", encoding="utf-8")
    return lock


# ------------------------------------------------------------------ todo

def markdown_anchors(path: Path) -> set[str]:
    anchors, seen = set(), {}
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        m = None if fenced else re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if m:
            t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1)).replace("`", "").replace("*", "")
            slug = re.sub(r"[^\w\- ]", "", t.strip().lower()).replace(" ", "-")
            n = seen.get(slug, 0)
            anchors.add(slug if n == 0 else f"{slug}-{n}")
            seen[slug] = n + 1
    return anchors


def check_todo(root: Path) -> list[str]:
    out = []
    mockup_md = root / "docs/design/mockup.md"
    anchors = markdown_anchors(mockup_md) if mockup_md.is_file() else set()
    if not mockup_md.is_file():
        out.append("todo: docs/design/mockup.md is missing")
    for f in sorted((root / "todo").rglob("TODO-*.md")):
        fenced = False
        lines = f.read_text(encoding="utf-8").splitlines()
        heads = [i for i, l in enumerate(lines) if re.match(r"^## ", l)]
        for n, line in enumerate(lines, 1):
            if FENCE_RE.match(line):
                fenced = not fenced
                continue
            m = None if fenced else DESIGN_LINE_RE.match(line)
            if not m:
                continue
            refs = MOCKUP_REF_RE.findall(m.group("body"))
            where = f"{rel(root, f)}:{n}"
            # The section this Design line sits in must carry the conformance micro-step.
            start = max((i for i in heads if i < n - 1), default=0)
            end = min((i for i in heads if i > n - 1), default=len(lines))
            items = [l for l in lines[start:end] if re.match(r"^\s*- \[[ x]\] ", l)]
            if not any("docs/design/mockup" in l and "design-lint" in l for l in items):
                out.append(f"todo: {where}: the section has no mockup conformance item (a checklist item citing "
                           "docs/design/mockup and scripts/design-lint.py; template in .claude/skills/create-todo/todo-template.md)")
            if not refs:
                out.append(f"todo: {where}: the Design line cites no docs/design/mockup.md#<anchor>; "
                           "every surface builds to the approved mockup (docs/design/mockup.md)")
            for a in refs:
                if a not in anchors:
                    out.append(f"todo: {where}: docs/design/mockup.md#{a} matches no heading in docs/design/mockup.md")
    return out


# ------------------------------------------------------------------ source ratchet

def scan_sources(root: Path) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {r: {} for r in RATCHET_RULES}
    files = []
    src = root / "src"
    if src.is_dir():
        files += [p for p in src.rglob("*") if p.suffix in (".ts", ".html", ".css") and not p.name.endswith(".test.ts")]
    files += [root / n for n in ("manifest.xml", "manifest.dev.xml") if (root / n).is_file()]
    for f in sorted(files):
        r = rel(root, f)
        if r in GENERATED:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if f.suffix != ".xml":
            n = len(COLOR_RE.findall(text))
            if n:
                counts["color-literal"][r] = n
            n = len(SVG_RE.findall(text))
            if n:
                counts["inline-svg"][r] = n
            n = sum(1 for m in FONT_RE.finditer(text) if not (m.group(1) and "var(--" in m.group(1)))
            if n:
                counts["font-family"][r] = n
        n = len(LEGACY_ICON_RE.findall(text))
        if n:
            counts["legacy-icon"][r] = n
    return counts


def baseline_path(root: Path) -> Path:
    return root / "docs/design/.lint-baseline.json"


def load_baseline(root: Path) -> dict[str, dict[str, int]]:
    f = baseline_path(root)
    if not f.is_file():
        return {r: {} for r in RATCHET_RULES}
    data = json.loads(f.read_text(encoding="utf-8")).get("rules", {})
    return {r: dict(data.get(r, {})) for r in RATCHET_RULES}


def compare(counts, base) -> list[str]:
    out = []
    for rule in RATCHET_RULES:
        for f in sorted(set(counts[rule]) | set(base[rule])):
            now, was = counts[rule].get(f, 0), base[rule].get(f, 0)
            if now > was:
                out.append(f"{rule}: {f} has {now}, the baseline allows {was}: use the design tokens and the icon registry "
                           "(docs/design/README.md), never raise the baseline")
            elif now < was:
                out.append(f"{rule}: {f} is down to {now} from {was}: shrink the baseline in this commit with "
                           "`python scripts/design-lint.py --update-baseline`")
    return out


def update_baseline(root: Path) -> list[str]:
    counts, base = scan_sources(root), load_baseline(root)
    grown = [ln for ln in compare(counts, base) if " the baseline allows " in ln]
    if grown and baseline_path(root).is_file():
        return grown
    data = {"schema": 1,
            "note": "Violations of the design gate that predate it (2026-09-27). Counts may only shrink; "
                    "scripts/design-lint.py refuses growth. See docs/design/README.md.",
            "rules": {r: dict(sorted(counts[r].items())) for r in RATCHET_RULES}}
    baseline_path(root).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return []


# ------------------------------------------------------------------ main

def run(root: Path) -> list[str]:
    tokens, problems = load_tokens(root)
    problems += check_icons(root)
    problems += check_mockup(root, tokens)
    problems += check_todo(root)
    problems += compare(scan_sources(root), load_baseline(root))
    return problems


def self_test() -> int:
    passed = failed = 0

    def check(name, cond, detail=""):
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"FAIL {name} {detail}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs/design/mockup/renders").mkdir(parents=True)
        (root / "assets/icons/src/pane").mkdir(parents=True)
        (root / "src/ui").mkdir(parents=True)
        (root / "todo/01-x").mkdir(parents=True)
        tokens = {"color": {"light": {"bg": "#ffffff", "text": "#1b1d22"}, "dark": {"bg": "#1b1d22", "text": "#eceef2"}}}
        (root / "docs/design/tokens.json").write_text(json.dumps(tokens), encoding="utf-8")
        (root / "docs/design/mockup.md").write_text("# M\n\n## Result card\n\n```\n## Not an anchor\n```\n", encoding="utf-8")
        board = '<div style="color: #1b1d22">\n<svg><path fill="#123456"></path></svg>\n</div>\n'
        (root / "docs/design/mockup/Reply.dc.html").write_bytes(board.encode())
        (root / "docs/design/mockup/canvas.json").write_text(json.dumps({"order": ["Reply.dc.html"]}), encoding="utf-8")
        (root / "docs/design/mockup/renders/Reply.png").write_bytes(b"png")
        (root / "docs/design/mockup/renders/manifest.json").write_text(json.dumps({"Reply.png": {
            "board": "Reply.dc.html", "boardSha256": sha256(root / "docs/design/mockup/Reply.dc.html"),
            "pngSha256": sha256(root / "docs/design/mockup/renders/Reply.png")}}), encoding="utf-8")
        relock_mockup(root, "v1")
        (root / "assets/icons/src/pane/a.svg").write_text("<svg></svg>", encoding="utf-8")
        (root / "src/ui/icons.ts").write_text("export const x = '<svg>';\n", encoding="utf-8")
        (root / "assets/icons/manifest.json").write_text(json.dumps({
            "sources": {"assets/icons/src/pane/a.svg": sha256(root / "assets/icons/src/pane/a.svg")},
            "outputs": {"src/ui/icons.ts": sha256(root / "src/ui/icons.ts")}}), encoding="utf-8")
        todo = root / "todo/01-x/TODO-01-x.md"
        conf = "- [ ] Match the docs/design/mockup renders. Done when: python scripts/design-lint.py exits 0.\n"
        todo.write_text("## 1. S\n\n**Design:** docs/design/taskpane.md#layout, docs/design/mockup.md#result-card -- states: all in spec\n\n" + conf, encoding="utf-8")
        (root / "src/a.css").write_text(".a { color: #ffffff; font-family: Poppins; }\n", encoding="utf-8")
        update_baseline(root)
        check("clean tree passes", run(root) == [], run(root))
        # a CRLF checkout of pinned text files (Windows, core.autocrlf) still passes
        mb = root / "docs/design/mockup/Reply.dc.html"
        mb.write_bytes(board.encode().replace(b"\n", b"\r\n"))
        check("the CRLF copy really differs in bytes", mb.read_bytes() != board.encode())
        check("line endings do not change a pinned hash", run(root) == [], run(root))
        mb.write_bytes(board.encode())

        # tokens
        bad = json.loads(json.dumps(tokens)); bad["color"]["dark"]["extra"] = "#000000"
        (root / "docs/design/tokens.json").write_text(json.dumps(bad), encoding="utf-8")
        check("token key mismatch is caught", any("keys differ" in p for p in run(root)))
        bad["color"]["light"]["extra"] = "red"
        (root / "docs/design/tokens.json").write_text(json.dumps(bad), encoding="utf-8")
        check("non-hex token is caught", any("is not #rrggbb" in p for p in run(root)))
        (root / "docs/design/tokens.json").write_text(json.dumps(tokens), encoding="utf-8")

        # icons
        (root / "assets/icons/src/pane/a.svg").write_text("<svg><path/></svg>", encoding="utf-8")
        check("changed icon source is caught", any("changed since the last build" in p for p in run(root)))
        (root / "assets/icons/src/pane/a.svg").write_text("<svg></svg>", encoding="utf-8")
        (root / "src/ui/icons.ts").write_text("export const x = 1;\n", encoding="utf-8")
        check("hand-edited registry is caught", any("edited by hand or is stale" in p for p in run(root)))
        (root / "src/ui/icons.ts").write_text("export const x = '<svg>';\n", encoding="utf-8")
        (root / "assets/icons/src/pane/b.svg").write_text("<svg></svg>", encoding="utf-8")
        check("unbuilt new icon is caught", any("is new since the last build" in p for p in run(root)))
        (root / "assets/icons/src/pane/b.svg").unlink()

        # mockup
        (root / "docs/design/mockup/Reply.dc.html").write_bytes(board.replace("#1b1d22", "#1b1d23").encode())
        probs = run(root)
        check("hand-edited artboard is caught", any("differs from the pinned" in p for p in probs), probs)
        check("stale render is caught", any("older Reply.dc.html" in p for p in probs), probs)
        check("non-token mockup color is caught", any("#1b1d23, which is not" in p for p in probs), probs)
        check("svg colors are exempt from the token rule", not any("#123456" in p for p in probs), probs)
        (root / "docs/design/mockup/Reply.dc.html").write_bytes(board.encode())
        (root / "docs/design/mockup/Extra.dc.html").write_text("x", encoding="utf-8")
        check("unpinned artboard is caught", any("Extra.dc.html is not pinned" in p for p in run(root)))
        (root / "docs/design/mockup/Extra.dc.html").unlink()

        # todo
        todo.write_text("## 1. S\n\n**Design:** docs/design/taskpane.md#layout -- states: all in spec\n", encoding="utf-8")
        check("Design line without a mockup ref is FATAL", any("cites no docs/design/mockup.md" in p for p in run(root)))
        todo.write_text("## 1. S\n\n**Design:** docs/design/mockup.md#not-an-anchor -- states: all in spec\n", encoding="utf-8")
        check("dead mockup anchor is caught (fenced headings are not anchors)", any("matches no heading" in p for p in run(root)))
        todo.write_text("```\n**Design:** docs/design/taskpane.md#layout\n```\n", encoding="utf-8")
        check("a fenced example is inert", not any(p.startswith("todo:") for p in run(root)))
        todo.write_text("## 1. S\n\n**Design:** docs/design/mockup.md#result-card -- states: all in spec\n\n- [ ] Build it.\n\n## 2. T\n\n" + conf, encoding="utf-8")
        check("a section without the conformance item is FATAL (a later section's item does not count)",
              any("no mockup conformance item" in p for p in run(root)), run(root))
        todo.write_text("## 1. S\n\n**Design:** docs/design/mockup.md#result-card -- states: all in spec\n\n" + conf, encoding="utf-8")

        # ratchet
        (root / "src/b.ts").write_text("el.style.color = '#abcdef'; x.innerHTML = '<svg></svg>';\n", encoding="utf-8")
        probs = run(root)
        check("new color literal is caught", any(p.startswith("color-literal: src/b.ts") for p in probs), probs)
        check("new inline svg is caught", any(p.startswith("inline-svg: src/b.ts") for p in probs), probs)
        check("update-baseline refuses growth", update_baseline(root) != [])
        (root / "src/b.ts").unlink()
        (root / "src/a.css").write_text(".a { color: var(--gm-text); font-family: var(--gm-font); }\n", encoding="utf-8")
        check("a fixed file must shrink the baseline", any("shrink the baseline" in p for p in run(root)))
        check("update-baseline accepts a shrink", update_baseline(root) == [] and run(root) == [], run(root))
        (root / "src/c.ts").write_text("const id = '#add-button'; const q = '#abc-x';\n", encoding="utf-8")
        check("selector ids are not colors", "src/c.ts" not in scan_sources(root)["color-literal"])
        (root / "manifest.xml").write_text('<bt:Image DefaultValue="https://x/assets/tool-icons/ai-tools-16.png"/>', encoding="utf-8")
        check("legacy icon path is counted", scan_sources(root)["legacy-icon"].get("manifest.xml") == 1)

    print(f"design-lint self-test: {passed + failed} cases, {failed} failed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--relock-mockup", metavar="VERSION")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root", default=str(REPO), help=argparse.SUPPRESS)
    a = ap.parse_args()
    root = Path(a.root)
    if a.self_test:
        return self_test()
    if a.relock_mockup:
        print(f"design-lint: pinned {rel(root, relock_mockup(root, a.relock_mockup))} to {a.relock_mockup}")
        return 0
    if a.update_baseline:
        grown = update_baseline(root)
        for g in grown:
            print(f"REFUSED {g}")
        if grown:
            print("design-lint: the baseline only shrinks; fix the new violations instead")
            return 1
        print(f"design-lint: baseline written to {rel(root, baseline_path(root))}")
        return 0
    problems = run(root)
    for p in problems:
        print(f"FATAL {p}")
    counts = scan_sources(root)
    total = sum(sum(v.values()) for v in counts.values())
    print(f"design-lint: {len(problems)} problem(s); {total} baselined legacy violation(s) left to burn down")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
