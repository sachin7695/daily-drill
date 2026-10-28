"""Shared question constructor for Daily Drill banks.

Each Q(...) is one four-option question. Rules:
  * `id` is permanent. Never renumber or reuse one. A materially different
    question gets a new id; an improved explanation bumps `rev`.
  * `answer` is zero-based (0 = A ... 3 = D).
  * `verify=True`: build.py runs `code` and checks that its stdout (plus the
    exception class name, if it raises) equals the correct choice.
  * `check="..."`: hidden code that build.py runs the same way, for answers
    that are calculations rather than the output of the shown code.
"""
from textwrap import dedent


def make_q(subject, store):
    def Q(id, topic, difficulty, choices, answer, key, why, trap, prompt=None,
          code=None, verify=False, check=None, mono=None, rev=1):
        code = dedent(code).strip("\n") if code else None
        if prompt is None:
            prompt = "What does this print?" if code else ""
        store.append(dict(
            id=id, revision=rev, subject=subject, topic=topic,
            difficulty=difficulty, prompt=prompt, code=code, choices=choices,
            correctIndex=answer, keyIdea=key, reasoning=why, commonTrap=trap,
            verify=verify, check=dedent(check).strip("\n") if check else None,
            monoChoices=bool(verify if mono is None else mono),
        ))
    return Q
