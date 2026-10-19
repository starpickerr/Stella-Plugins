# Stella-Plugins

First-party business plugins for [Stella](https://github.com/starpickerr/Stella). Core ships the runtime (`core.plugins` + `stella-plugin-runner`); this repository ships the default business packages.

| Plugin | Contract | Notes |
| --- | --- | --- |
| `plugins/bills` | `stella.bills@1` | Ledger, statements, idempotent receipts |
| `plugins/calendar` | `stella.calendar@1` | Events/categories; Apple sync stays in Core |
| `plugins/tasks` | `stella.tasks@1` | Todos/reminders; host reconciles scheduler links |
| `plugins/email` | `stella.email@1` | IMAP credentials, folders, cursors |
| `plugins/elearning` | `stella.elearning@1` | Courses, sync, file sync |
| `plugins/briefing` | `stella.briefing@1` | Rules, snapshots, outbox; sources via Core directory |
| `plugins/automation` | `stella.automation@1` | Rules/mutations; Core keeps lease/dispatch |

Packages must not import Stella `agent.*`. Catalog digests live in `catalog/official.json`.
