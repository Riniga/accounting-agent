# Glossary

The organisations keep their books in Swedish; the core's code and documentation are in
English ([`docs/standards/coding.md`](../standards/coding.md)). This table maps the terms.
The English name in the right-hand column is the one used in the code.

| Swedish (organisation files) | English (core) | Meaning |
|---|---|---|
| bokföring | books (`Books`) | An organisation's chart of accounts, opening balances and vouchers for one fiscal year |
| verifikation | voucher (`Voucher`) | One recorded business event, with its posting lines and supporting documents |
| verifikationsnummer | voucher number | The voucher's sequence number within its series |
| verifikationsserie | voucher series | A separate number sequence, e.g. K for customer invoices and B for bank; optional |
| kontering, konteringsrad | posting line (`PostingLine`) | One account with a debit or credit amount on a voucher |
| konto | account (`Account`) | An account number (four digits, BAS) and its name |
| kontoplan | chart of accounts | The accounts an organisation uses |
| kontobas, BAS | BAS chart | The complete Swedish standard chart of accounts, as a reference |
| ingående balans (IB) | opening balance (`OpeningBalance`) | An account's balance at the start of the fiscal year |
| utgående balans, saldo | balance | Opening balance plus the year's postings |
| debet / kredit | debit / credit | The two sides of a posting; the core counts debit as positive |
| belopp | amount | Always `Decimal`, never a floating-point number |
| underlag | supporting document | The receipt, invoice or bank page that backs a voucher |
| anteckning | note | Free text on a voucher |
| räkenskapsår | fiscal year | The accounting year; a calendar year for the current organisations |
| balanskonto | balance account | An asset or liability/equity account (classes 1–2) |
| resultatkonto | income-statement account | A revenue or cost account (classes 3–8) |
| personnummer | personal identity number | Swedish national ID number — masked in all core output |
| kassör | treasurer | The organisation's person responsible for the books |
| revisor | auditor | Reviews the books once a year |
| fynd | finding (`Finding`) | One result of a check: severity, rule, location and message |

**Severities** of findings, following Helsingborgs Judoklubb's `kontroll.py`:
- *FEL* → **error** (the books are broken; exit code 1);
- *VARNING* → **warning** (looks wrong; review it);
- *INFO* → **info**.
