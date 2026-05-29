---
applyTo: "src/**/*.py"
---

Preserve PBIR and TMDL schema fidelity.

Any slot mapping change across SUM, CNT, AVG, KEY, or DATE requires a regression test.

Directory renames on Windows must use the retry helper to tolerate transient endpoint-security locks.
