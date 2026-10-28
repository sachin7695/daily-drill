"""Validate the question banks and write app/banks/*.json.

Usage:  python3 build.py
Exits non-zero if any question is malformed or any verified snippet's real
output does not match its marked answer.
"""
import contextlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "content"))

import python_bank  # noqa: E402

BANKS = [("python", "Python", python_bank)]
DIFFICULTIES = {"easy", "medium", "hard"}
ID_RE = re.compile(r"^[A-Z]{2,4}-[A-Z]{3}-\d{3}$")
REQUIRED = ["id", "revision", "topic", "difficulty", "prompt", "choices",
            "correctIndex", "keyIdea", "reasoning", "commonTrap"]


def run_snippet(code):
    """Run code in a fresh namespace; return stdout plus the exception name if it raised."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        try:
            exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
        except BaseException as e:  # noqa: BLE001 — the exception name is the expected output
            print(type(e).__name__)
    return "\n".join(line.rstrip() for line in buf.getvalue().strip().splitlines())


def check_bank(bank_id, module):
    errors, verified = [], 0
    topics = {t for t, _ in module.TOPICS}
    seen = set()
    for q in module.QUESTIONS:
        qid = q.get("id", "?")
        for field in REQUIRED:
            if q.get(field) in (None, ""):
                errors.append(f"{qid}: missing {field}")
        if not ID_RE.match(qid):
            errors.append(f"{qid}: bad id format")
        if qid in seen:
            errors.append(f"{qid}: duplicate id")
        seen.add(qid)
        if q["topic"] not in topics:
            errors.append(f"{qid}: unknown topic {q['topic']}")
        if q["difficulty"] not in DIFFICULTIES:
            errors.append(f"{qid}: bad difficulty")
        if len(q["choices"]) != 4 or len(set(q["choices"])) != 4:
            errors.append(f"{qid}: need 4 distinct choices")
        if not 0 <= q["correctIndex"] < 4:
            errors.append(f"{qid}: correctIndex out of range")
        if q["verify"]:
            if not q.get("code"):
                errors.append(f"{qid}: verify without code")
                continue
            got = run_snippet(q["code"])
            want = q["choices"][q["correctIndex"]].strip()
            if got != want:
                errors.append(f"{qid}: snippet printed {got!r}, marked answer is {want!r}")
            for i, c in enumerate(q["choices"]):
                if i != q["correctIndex"] and c.strip() == got:
                    errors.append(f"{qid}: distractor {i} also matches the real output")
            verified += 1
    return errors, verified


def main():
    out_dir = ROOT / "app" / "banks"
    out_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    for bank_id, title, module in BANKS:
        errors, verified = check_bank(bank_id, module)
        for e in errors:
            print("ERROR", e)
        failed |= bool(errors)
        qs = [{k: v for k, v in q.items() if k != "verify" and v is not None}
              for q in module.QUESTIONS]
        bank = {"id": bank_id, "title": title, "python": sys.version.split()[0],
                "topics": [{"id": t, "title": n} for t, n in module.TOPICS],
                "questions": qs}
        (out_dir / f"{bank_id}.json").write_text(json.dumps(bank, indent=1, ensure_ascii=False))
        by_diff = {d: sum(q["difficulty"] == d for q in qs) for d in ("easy", "medium", "hard")}
        print(f"{bank_id}: {len(qs)} questions, {verified} snippets executed and matched, {by_diff}")
    if not failed:
        write_www(out_dir)
    sys.exit(1 if failed else 0)


def write_www(banks_dir):
    """Wrap app/index.html (an artifact page body) into a full document for the Android app."""
    www = ROOT / "www"
    (www / "banks").mkdir(parents=True, exist_ok=True)
    body = (ROOT / "app" / "index.html").read_text()
    head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
            'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
    (www / "index.html").write_text(head + body + "\n</body></html>\n")
    for f in banks_dir.glob("*.json"):
        (www / "banks" / f.name).write_text(f.read_text())
    print(f"wrote {www}/index.html for the Android build")


if __name__ == "__main__":
    main()
