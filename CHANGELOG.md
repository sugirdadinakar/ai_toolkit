# Changelog

All notable changes to **ai-toolkit** are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-10-28

The Ultimate PM Toolkit — a full product-management workflow for Claude Code:
10 agents, 9 commands, and a broad set of skills, installable as a plugin via
its bundled marketplace.

### Plugin
- `.claude-plugin/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — marketplace manifest (enables `/plugin marketplace add` + `/plugin install`)

### Agents (`agents/`)
- **cpto-review** — brutally honest, commercially-aware executive (CPTO) review of PRDs, architectures, and strategy
- **prd-reviewer** — senior-PM, severity-ranked critique of a PRD/spec/epic
- **discovery-interviewer** — build / role-play / critique discovery interviews (Mom Test)
- **customer-brief-analyst** — 1-page pre-meeting account intel brief across connected tools
- **data-brief-analyst** — structured insight brief from a provided dataset/file
- **data-storyteller** — narrative metrics brief from live Amplitude or pasted data
- **market-research-analyst** — market sizing (TAM/SAM/SOM) + competitive intelligence with citations
- **prototype-builder** — zero-build interactive HTML prototypes
- **ux-designer** — user flows, information architecture, and UX critique
- **voice-of-customer** — synthesize ambient customer signal into confidence-ranked VoC themes

### Commands (`commands/`)
- `/prd` — draft a PRD from a problem/idea
- `/jtbd` — Jobs-to-be-Done analysis
- `/discovery` — discovery plan + non-leading interview guide
- `/add-mcp` — how to connect MCP servers
- `/competitive-analysis` — research & analyze a competitor (WebSearch + Porter's Five Forces)
- `/customer-brief` — pre-meeting account intel brief (delegates to customer-brief-analyst)
- `/decision-brief` — 1-page decision brief with a clear recommendation
- `/experiment` — design, plan & analyse A/B tests (Amplitude-aware)
- `/feature-request` — intake & triage a feature request (RICE, P0–Decline)

### Skills (`skills/<name>/SKILL.md`)
- **prd-writing**, **research-synthesis**, **decision-brief**, **churn-signal**,
  **debate**, **design-an-interface**, **impact-sizing**, **interview-analysis**,
  **learn**, **recall**, **roadmap-narrative**, **sprint-health**,
  **parallel-prototype**, **rapid-prototype**, **pdf**, **docx**, **pptx**,
  **web-browser**, **xlsx**

### Skill companion files & tooling
- **pdf** — `REFERENCE.md`, `FORMS.md`
- **docx** — `docx-js.md`, `ooxml.md`, `ooxml/scripts/{unpack,pack}.py`
- **pptx** — `html2pptx.md`, `ooxml.md`, the `html2pptx/` library, `ooxml/scripts/{unpack,pack,validate}.py`, `scripts/{inventory,replace,rearrange,thumbnail}.py`
- **impact-sizing** — `README.md`, `generate_impact_sizing.py`
- **interview-analysis** — `examples/`, `templates/`
- **parallel-prototype** / **rapid-prototype** — bundled HTML `templates/` (+ `CLAUDE.md` conventions)
- **web-browser** — `tools/` built on `puppeteer-core` (`package.json` + `package-lock.json`)

### Flat reference files (`skills/*.md`)
Content/reference docs (not auto-loaded as skills): `jtbd.md`,
`opportunity-tree.md`, `prd.md`, `prioritization.md`, `probtoprd.md`,
`user-stories.md`, `recall.md`.

### Docs
- `README.md` with full directory tree, command/skill/agent catalogs, and install instructions
- `.gitignore`

### Known gaps
- **xlsx** references a `recalc.py` helper that is not yet included.
- `skills/learn.zip` and `skills/rapid-prototype.zip` are packaged artifacts tracked in the repo; remove if unintended.
- Several data-oriented skills/commands need connectors authorized via `/mcp` (Amplitude, Intercom, Jira, Slack) to pull live data; they degrade gracefully when a source is unavailable.

[1.1.0]: https://github.com/sugirdadinakar/ai_toolkit
