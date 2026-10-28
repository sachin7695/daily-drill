# Daily Drill

A phone-friendly practice app for Python and ML interview prep.

```
content/python_bank.py   question source (edit here)
build.py                 validates banks, runs code snippets, writes app/banks/*.json
app/index.html           the app (Home / Library / Progress, sprints, review queue)
app/banks/python.json    generated, do not edit by hand
```

## Adding or changing questions

1. Add a `Q(...)` to `content/python_bank.py` (or a new `content/<subject>_bank.py`, registered in `BANKS` in build.py and in `BANKS` at the top of the script in index.html).
2. Run `python3 -I build.py`. It fails if an id is duplicated, a field is missing, or a `verify=True` snippet's real output differs from the marked answer.
3. Republish `app/index.html` with `banks/<id>.json` as a supporting file (ask Claude to "republish Daily Drill").

## Id and revision rules

- Ids are permanent. Never renumber or reuse one. A materially different question gets a new id.
- Improving an explanation means bumping `rev`. If you change which answer is correct, bump `rev` too: anyone who had it solved gets it back in their review queue.
- The position of `answer` doesn't matter. The app shuffles the options every time it shows a question.

## Android app

Every push to `main` builds a signed APK on GitHub Actions (`.github/workflows/android.yml`) and attaches it to a new GitHub Release.

- The web code is the same `app/index.html`. `build.py` wraps it into `www/`, and Capacitor packages that.
- The signing key is kept privately offline and in the repo secrets `ANDROID_KEYSTORE_B64` and `ANDROID_KEYSTORE_PASSWORD`. **Don't lose it.** Without the same key, an update can't install over the old app, and uninstalling deletes its progress.
- The phone app stores progress on the phone and works offline. Use Progress → Back up / Restore to move progress between the phone and the Claude-hosted page.
- `make_icons.py` redraws `assets/` (it needs Pillow).

## Progress storage

Answers save to the browser right away. When you're signed in as the artifact owner, they also sync to the artifact's database (`progress/<question id>`, `meta/activity`). The access rules let only the owner read or write it, so your phone and laptop stay in step.
