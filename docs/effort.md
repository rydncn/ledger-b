| Piece of work | What it delivered | Sessions | Peak context per session | Wall clock |
| --- | --- | --- | --- | --- |
| Environment repair | Diagnosed the failing setup script (older `uv` shadowing the pinned one, so Python 3.15.2 was unknown); proposed the fix and installed by hand | 1 | ~25k tokens | 5 min |
| Core: money, encoding, config, store | Exact integer money parsing and formatting; encoding detection; TOML layouts and rules with validation; SQLite store with private file modes, serialised writes and fingerprint uniqueness | 1 | ~60k tokens | 15 min |
| Importers | Streaming CSV reader with row repair and per-line problems; tolerant OFX reader for SGML and XML; fingerprinting; import orchestration with strict mode | 1 | ~80k tokens | 15 min |
| Rules, reports, output, CLI | First-match categorisation with explanations; monthly category and payee reports; table/CSV/JSON output with colour rules and formula guarding; all eleven commands | 1 | ~100k tokens | 15 min |
| Tests | 163 tests: unit, end-to-end CLI via subprocess, duplicate handling, two-process concurrency, 100k-row import, privacy of messages, file permissions | 1 | ~120k tokens | 20 min |
| Docs, CI, samples | README, configuration reference, decisions record, MIT licence, three-OS CI workflow, the three sample files byte-exact | 1 | ~130k tokens | 10 min |
| CI fix | Windows reports the NUL device as a terminal, so `tally forget` prompted and exited 0 in a scheduled job; an unanswered prompt is now a refusal with the `--yes` hint. Bumped deprecated action versions | 1 | ~145k tokens | 10 min |
| Running-balance check | Optional `balance` layout column; each row checked against its neighbour with statement order inferred; mismatches noted by line; seven tests; docs | 1 | ~160k tokens | 15 min |
| Import history and undo | `tally imports` lists every import with its counts; `tally undo ID` removes exactly the rows that import added, with confirmation; tests and docs | 1 | ~175k tokens | 10 min |
| **Total** | | **1** | **~175k tokens** | **~115 min** |

## Defects found and fixed along the way

- `executescript` silently committed the open `BEGIN IMMEDIATE` transaction, so the first `COMMIT` failed with "no transaction is active". Found by the first smoke test of `tally account add`; fixed by executing the schema statement by statement.
- The sample row `=HYPERLINK("http://example.invalid","Refund")` was skipped as unreadable because its unquoted comma split the row into six fields. Found by smoke-testing the sample import; fixed by folding surplus fields into the description with a note on the line.
- `(3.40)` in the Money Out column was imported as money in. Found by checking the sample's Balance column, which drops by 3.40; fixed by treating signs in dedicated direction columns as presentation.
- `--5` and `£--5` parsed as positive 5 because the sign check after a currency mark could run twice. Found by a parametrised rejection test; fixed by tracking whether a sign was already seen.
- Global options (`--color`, `--config`, `--data`) were rejected after the command name, which is where people type them. Found by the CLI colour test; fixed by accepting them in both positions.
- Payee spelling ties were resolved by alphabetical order, so the displayed payee name depended on sort quirks. Found by the top-payees test; fixed by preferring the most frequent spelling and, on a tie, the first seen.
- Python 3.13+ no longer raises on NUL bytes in CSV, so a binary-ish file passed through as text. Found by the NUL test failing to raise; fixed by reporting rows containing NUL as binary data.
- On Windows, `isatty()` is true for the NUL device, so `tally forget` in a scheduled job prompted, hit end-of-input and exited 0 instead of refusing without `--yes`. Found by the Windows CI job (a first attempt that only changed the test fixture failed the same way, which ruled out the inherited-console explanation); fixed by treating an unanswered prompt as a refusal with exit code 2.
- The first version of the wrong-sign balance test used identical amounts on every row, which a flipped sign cannot distinguish from a newest-first statement, and a pipe to `tail` hid its failure from the shell so it was pushed red. Found by re-reading the failing assertion; fixed by varying the amounts and running checks with `pipefail`.
