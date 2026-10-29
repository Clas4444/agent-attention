# Windows checkpoint follow-up

The first 0.1.1 push, bda6bfa, passed both Ubuntu jobs but failed both Windows
jobs in [validation run 40715495499](https://github.com/Clas4444/agent-attention/actions/runs/40715495499).
The optional checkpoint helper rejected ordinary runner temporary paths as
aliases: `Path.absolute()` and `Path.resolve()` differ when Windows uses an
8.3 short username such as RUNNER~1. Local paths had not exposed this difference.

The fix inspects path entries for symbolic links and Windows reparse points
instead of comparing resolved spelling. The plain-file and hardlink checks
remain. A real GetShortPathNameW regression initializes state through a short
parent name and checks the file through its long name. It runs on Windows;
platforms without Windows short names skip that specific test.

Local verification: 30/30 tests pass on Windows Python 3.14 and 3.12, including
the new short-name regression, with generated resources and diff checks passing.
No model trials were repeated for this filesystem-only fix. Earlier token
measurements and their source hashes remain historical measurements of the
frozen behavior snapshot; their reported sample counts are unchanged.
