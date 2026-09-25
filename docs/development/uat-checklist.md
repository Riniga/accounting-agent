# Stability Checklist (UAT)

## Purpose

A lightweight, repeatable manual pass to confirm the system is stable across every real
execution path: local development, any CLI/script execution, the CI/CD deploy pipeline,
and production. It complements — does not replace — the automated test suite: automated
tests verify code correctness in isolation, this verifies the real, wired-together system
(real external auth, the real deploy pipeline, real browser rendering, …).

Run it after any change touching deployment, pipeline execution, or cross-app
configuration, and periodically to catch drift (an expired credential, a removed
environment variable, an idle-unloaded service, etc.).

## How to use

- Each row is one check: do the steps, compare against the expected result.
- Not every row needs to be run every time — use judgement for what the current change
  could have affected. Before a stakeholder demo, run all of them.
- A failing row is a signal to stop and triage, not to note and move on — log it wherever
  this project tracks issues before continuing.
- Keep this file current as new environments, apps, or execution paths are added.

## Checklist

<!-- Replace with your own project's real checks. Group by execution path
     (local dev / CLI / CI deploy / production), and for each row: what to do, and the
     expected result. -->

| # | Area | Steps | Expected result |
|---|------|-------|------------------|
| 1 | Local development | | |
| 2 | CLI / script execution | | |
| 3 | CI/CD deploy pipeline | | |
| 4 | Production | | |
