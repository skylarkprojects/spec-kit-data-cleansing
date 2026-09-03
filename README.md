<div align="center">
    <img src="media/logo_large.webp" alt="Spec Kit Logo" width="200" height="200"/>
    <h1>🌱 Spec Kit — Data Cleansing Edition</h1>
    <h3><em>Define what "clean" means before you clean it — with any AI coding agent.</em></h3>
</div>

<p align="center">
    <strong>A fork of <a href="https://github.com/github/spec-kit">GitHub's Spec Kit</a>, retargeted from spec-driven <em>software</em> delivery to spec-driven <strong>data cleansing</strong>: a domain-agnostic constitution → target-data-model → audit → specify → plan → tasks → implement pipeline for bringing raw datasets into compliance with a target schema, with an explicit, machine-checked approval gate between every stage.</strong>
</p>

<p align="center">
    <a href="https://github.com/skylarkprojects/spec-kit-data-cleansing/releases"><img src="https://img.shields.io/github/v/release/skylarkprojects/spec-kit-data-cleansing" alt="Latest Release"/></a>
    <a href="./LICENSE"><img src="https://img.shields.io/github/license/skylarkprojects/spec-kit-data-cleansing" alt="License"/></a>
</p>

> [!NOTE]
> This repository does **not** contain any target schema, vocabulary, or dataset content of its own — that's deliberate. See [`MIGRATION.md`](MIGRATION.md) for exactly what changed from upstream Spec Kit, and [`docs/methodology-overview.md`](docs/methodology-overview.md) for how the pieces below fit together.

---

## Table of Contents

- [🧹 What is Spec-Driven Data Cleansing?](#-what-is-spec-driven-data-cleansing)
- [⚡ Quickstart](#-quickstart)
- [📁 Directory Layout](#-directory-layout)
- [🚦 The Stage-Gate Rule](#-the-stage-gate-rule)
- [🩺 Data Quality Skills: Intake & Issue Triage](#-data-quality-skills-intake--issue-triage)
- [🧱 Built on Spec Kit](#-built-on-spec-kit)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn More](#-learn-more)
- [💬 Support](#-support)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

## 🧹 What is Spec-Driven Data Cleansing?

Spec-driven development treats specifications as executable — the spec, not the code,
drives the outcome. This fork applies the same discipline to a different problem: turning
a raw, messy dataset into one that verifiably complies with a target data model, with
every transformation logged, every ambiguity flagged rather than guessed away, and every
stage requiring an explicit human approval before the next one may begin.

Six artefacts carry a dataset from "here's a file someone handed us" to "done":

| # | Artefact | Answers |
|---|---|---|
| 1 | `constitution.md` | What are our non-negotiable rules — raw immutability, transformation logging, ambiguous-value handling, provenance, escalation? |
| 2 | `target-data-model.md` | What schema must every cleaned dataset comply with? |
| 3 | `audit-report.md` | What's actually in this raw file? (no cleaning, no mapping) |
| 4 | `spec.md` | What is this dataset, and what does "done" mean for it? |
| 5 | `plan.md` | Field-by-field: how does raw become compliant, and what are the gaps/risks? |
| 6 | `tasks.md` | The plan broken into discrete, independently verifiable cleaning operations |

`05-implement.md` executes only an *approved* `tasks.md`, logging every operation to an
append-only, tamper-evident changelog — nothing here knows or cares what your target
schema, vocabulary, or dataset actually is. All of that is supplied per-project under
`instances/<name>/`.

## ⚡ Quickstart

These prompts are plain Markdown — hand them to your AI coding agent directly (paste into
Claude Code, or open as a file and ask your agent to follow it). No CLI install is
required for the methodology itself.

```text
1. Give your agent prompts/00-init.md
   → interviews you to fill in instances/<name>/constitution.md and
     instances/<name>/target-data-model.md; won't finish until both pass
     scripts/validate_against_model.py check-completeness

2. Give your agent prompts/01-audit.md, pointing at a raw dataset file
   → profiles it (scripts/profile_dataset.py) and writes audit-report.md
   → approve it: python scripts/stage_gate.py approve <entry.yaml> --stage audit --by <name>

3. prompts/02-specify.md → spec.md   (what "done" means, read against the target model)
4. prompts/03-plan.md    → plan.md   (field-by-field mapping + gap/risk assessment)
5. prompts/04-tasks.md   → tasks.md  (discrete, independently verifiable operations)
6. prompts/05-implement.md          (executes only an approved tasks.md, logs every
                                      operation via scripts/changelog.py)
```

Each stage is gated on the previous one being explicitly **approved** in the dataset's
registry entry — not merely present. See [The Stage-Gate Rule](#-the-stage-gate-rule).

## 📁 Directory Layout

```text
/templates       constitution / target-data-model / spec / plan / tasks templates
/prompts          00-init.md … 05-implement.md
/scripts           profile_dataset.py, validate_against_model.py, changelog.py, stage_gate.py
/registry            schema.yaml — what every dataset registry entry must record
/instances             README + an empty stub — your project's filled-in constitution,
                         target data model, and dataset registry live here, never in the package
/docs                    methodology-overview.md
```

## 🚦 The Stage-Gate Rule

A stage's artefact *existing* is not the same as it being *approved*. Every dataset has
one registry entry (`instances/<name>/registry/<dataset_id>.yaml`, shaped by
[`registry/schema.yaml`](registry/schema.yaml)) recording an explicit
`status: draft | approved | rejected` per stage:

```bash
python scripts/stage_gate.py check instances/<name>/registry/<id>.yaml --stage plan
# BLOCKED: 'plan' requires 'specify' to be approved (currently: draft).

python scripts/stage_gate.py approve instances/<name>/registry/<id>.yaml --stage specify --by <name>
python scripts/stage_gate.py check instances/<name>/registry/<id>.yaml --stage plan
# OK: 'specify' is approved — 'plan' may proceed.
```

Every prompt in `/prompts` runs this check before doing anything else, and
`05-implement.md` hard-refuses to touch a dataset whose `tasks.md` isn't approved.

## 🩺 Data Quality Skills: Intake & Issue Triage

Two extensions ship data-centric "skills" on top of the core pipeline, installed the same
way any Spec Kit extension is:

```bash
specify extension add intake   # go/needs-clarification/kill a candidate dataset
                                 # BEFORE it enters 01-audit.md
specify extension add issue    # assess/resolve/verify a data quality issue found
                                 # AFTER a dataset's implement stage is already approved
```

See [`extensions/intake/README.md`](extensions/intake/README.md) and
[`extensions/issue/README.md`](extensions/issue/README.md).

## 🧱 Built on Spec Kit

This is a fork of [github/spec-kit](https://github.com/github/spec-kit) — the constitution
→ specify → plan → tasks → implement discipline, the stage-by-stage approval mindset, and
the underlying `specify` CLI (installer, extensions, presets, bundles, 30+ AI agent
integrations) all come from there. [`MIGRATION.md`](MIGRATION.md) documents exactly what
was renamed, generalized, newly created, or dropped in this fork, file by file.

The original software-delivery methodology and its CLI still work unmodified in this
repo — nothing about generalizing the six artefacts required touching
`src/specify_cli/`, `presets/`, `workflows/`, or the original `templates/commands/*.md`.
If you want to use this fork's CLI for an actual **software** project (not data
cleansing), the install/reference docs under [`docs/`](docs/) still apply — the CLI
commands, extensions, presets, and bundles are unchanged from upstream — just point the
install command at this fork instead:

```bash
uv tool install specify-cli --from git+https://github.com/skylarkprojects/spec-kit-data-cleansing.git@vX.Y.Z
specify init my-project --integration copilot
```

## 🔧 Prerequisites

- **Linux/macOS/Windows**
- An AI coding agent — for the `/prompts` methodology, any agent that can read a Markdown
  file and follow instructions works; for the `specify` CLI (extensions/presets/bundles),
  see the [supported integrations reference](docs/reference/integrations.md).
- Only needed if you use the `specify` CLI (installing `intake`/`issue`, or the original
  software workflow): [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/),
  [Python 3.11+](https://www.python.org/downloads/), and [Git](https://git-scm.com/downloads).

## 📖 Learn More

- **[Methodology Overview](docs/methodology-overview.md)** — the six artefacts and the stage-gate rule, in under 500 words
- **[spec-driven.md](spec-driven.md)** — the deep-dive companion: why the pipeline is shaped this way, a worked example, and how each principle is mechanically enforced
- **[MIGRATION.md](MIGRATION.md)** — exactly what changed from upstream Spec Kit, and why

## 💬 Support

For issues specific to this fork (the data cleansing methodology, `intake`/`issue`
extensions, or the migration), open an issue at
[skylarkprojects/spec-kit-data-cleansing](https://github.com/skylarkprojects/spec-kit-data-cleansing/issues).
For anything about the underlying CLI, extension system, or the original software
methodology, the upstream project at
[github/spec-kit](https://github.com/github/spec-kit) is the authoritative source.

## 🙏 Acknowledgements

This fork stands entirely on the work of the [Spec Kit](https://github.com/github/spec-kit)
maintainers and community, and — per upstream's own acknowledgement — is heavily
influenced by the work and research of [John Lam](https://github.com/jflam).

## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to
the [LICENSE](./LICENSE) file for the full terms.
