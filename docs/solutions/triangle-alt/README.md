# Triangle

Baseline graded solution for `triangle`.

The single man receives `n`, computes `n × (n + 1) / 2`, sends the result,
and halts. `build.py` is the reproducible source of `triangle.man`.
`official-submission.json` records the first verified server result without
credentials.

```bash
python3 solutions/triangle/build.py --check
make verify-triangle
python3 scripts/submit.py submit triangle solutions/triangle/triangle.man --dry-run
python3 scripts/submit.py submit triangle solutions/triangle/triangle.man --wait
```

The submission client reads `ICFPC2026_API_KEY` when set, otherwise it looks
up the `service=icfpcontest2026, credential=api-key` entry in the OS secret
store. Never put the key in this directory.
