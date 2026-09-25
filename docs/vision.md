# Vision

## Purpose

Accounting Agent is a shared, AI-assisted bookkeeping core for small non-profit
organisations. It lets one codebase do the routine financial administration for several
organisations while each organisation's data, rules and permissions stay strictly separate.

The original project idea is kept unchanged as historical input in
[`initial-idea.md`](initial-idea.md).

---

## Desired outcome

> **A shared AI-based financial administrator that can work for several organisations
> through the same codebase, with strictly separated data, rules and permissions.**

Today three organisations — JudoSyd, Helsingborgs Judoklubb and Aktivitet Förebygger — each
run their own, independently developed AI-assisted bookkeeping project. The same
functionality (import, matching, posting, validation, reporting, integrations, AI
instructions) is built and maintained three times. This repository is the common core those
projects are rebuilt to consume; each consuming project then feeds needs back to the core so
that more work can be delegated to it over time.

The project should support an agent that can:

* collect financial source material (bank statements, PDFs, invoices, receipts, e-mail,
  payroll input)
* identify new transactions and match them against supporting documents
* propose or carry out postings according to the organisation's chart of accounts and rules
* validate the books and produce reports
* handle recurring administrative processes, including payroll where an organisation needs it
* judge its own certainty, ask a human when it is unsure or an operation is risky, and
  continue once the decision is made
* leave an audit trail that answers: *what did the agent do, why, and based on which
  document?* — supporting each organisation's annual audit

People should mainly handle **exceptions, approvals and decisions** — not routine
administration.

---

## Principles

* **Data belongs to the organisation.** Organisations' financial data is never mixed. This
  repository holds code, models and synthetic test data only
  ([ADR-003](architecture/decisions/ADR-003-no-real-data-in-core-repo.md)).
* **Code belongs to the platform.** General functionality is implemented once, here. The
  core knows nothing about any specific organisation.
* **Configuration over customisation.** Differences between organisations are expressed as
  configuration and rules, not as separate code branches.
* **AI decides, code executes.** The LLM is used for understanding, classification and
  judgement; deterministic Python does file operations, bookkeeping operations, validation,
  calculations and integrations.
* **Human-in-the-loop at risk.** Uncertain or sensitive operations require a human decision.
* **Everything is auditable.** The agent's significant decisions and actions can be reviewed
  afterwards.
* **Extract, don't rewrite.** Existing working solutions are the starting point.
  Functionality moves into the core only when there is a working, concrete function to
  generalise — never to achieve a tidy architecture.
* **Grow one MVP at a time**, following the project's development methodology
  ([ADR-001](architecture/decisions/ADR-001-adopt-development-methodology.md)).
