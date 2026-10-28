# ai-toolkit

The Ultimate PM Toolkit for Claude Code — product-management commands, skills, and agents that cover the whole PM workflow: discovery, specs, research synthesis, customer intel, data analysis, market research, UX design, and prototyping.

## What's inside

```
ai-toolkit/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   └── marketplace.json         # Marketplace manifest (enables /plugin install)
├── commands/                    # Slash commands (you invoke these)
│   ├── prd.md                   # /prd       — draft a PRD from a problem/idea
│   ├── jtbd.md                  # /jtbd      — Jobs-to-be-Done analysis
│   ├── discovery.md             # /discovery — discovery plan + interview guide
│   ├── add-mcp.md               # /add-mcp   — how to connect MCP servers
│   ├── competitive-analysis.md  # /competitive-analysis — analyze a competitor
│   ├── customer-brief.md        # /customer-brief — pre-meeting account intel brief
│   └── decision-brief.md        # /decision-brief — 1-page decision brief w/ recommendation
├── skills/                      # Skills (auto-trigger from context)
│   ├── prd-writing/SKILL.md         # Writing and refining PRDs
│   ├── research-synthesis/SKILL.md  # Synthesizing user research into insights
│   ├── decision-brief/SKILL.md      # 1-page decision brief with a recommendation
│   ├── churn-signal/SKILL.md        # Account health score + recommended intervention
│   ├── debate/SKILL.md              # Champion vs Sceptic stress-test of an idea
│   ├── design-an-interface/SKILL.md # "Design it twice" — parallel interface designs
│   ├── impact-sizing/               # ARR impact sizing → Excel workbook
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── generate_impact_sizing.py
│   ├── interview-analysis/          # Parallel interview analysis (Teresa Torres)
│   │   ├── SKILL.md
│   │   ├── examples/parallel-dispatch-example.md
│   │   └── templates/{interview,synthesis}-template.md
│   ├── learn/SKILL.md               # Deep-dive research saved as reusable knowledge
│   ├── recall/SKILL.md              # Retrieve knowledge saved by the learn skill
│   ├── roadmap-narrative/SKILL.md   # One roadmap → exec/eng/customer narratives
│   ├── sprint-health/SKILL.md       # Jira sprint health check + shareable status
│   ├── parallel-prototype/          # 3 structurally different HTML prototypes, compared
│   │   ├── SKILL.md
│   │   └── templates/{blank_prototype_template,DesignSystem}.html
│   ├── rapid-prototype/             # Zero-build HTML prototyping kit
│   │   ├── SKILL.md
│   │   └── templates/{blank_prototype_template.html,DesignSystem.html,CLAUDE.md}
│   ├── pdf/                         # PDF toolkit — extract, create, merge/split, forms
│   │   ├── SKILL.md
│   │   ├── REFERENCE.md             # advanced (pypdfium2, pdf-lib) + troubleshooting
│   │   └── FORMS.md                 # filling PDF forms
│   ├── docx/                        # Word docs — create, edit, tracked changes, redlining
│   │   ├── SKILL.md
│   │   ├── docx-js.md               # creating .docx with docx-js
│   │   ├── ooxml.md                 # OOXML editing + tracked-change patterns
│   │   └── ooxml/scripts/{unpack,pack}.py
│   ├── pptx/                        # PowerPoint — create (html2pptx/template), edit, analyze
│   │   ├── SKILL.md
│   │   ├── html2pptx.md
│   │   ├── ooxml.md
│   │   ├── html2pptx/{package.json,index.js}
│   │   ├── ooxml/scripts/{unpack,pack,validate}.py
│   │   └── scripts/{inventory,replace,rearrange,thumbnail}.py
│   ├── web-browser/                 # Remote-control Chrome via CDP (puppeteer-core)
│   │   ├── SKILL.md
│   │   └── tools/{start,nav,eval,screenshot,pick}.js + package.json + package-lock.json
│   └── xlsx/SKILL.md                # Spreadsheets — formulas, formatting, recalc, analysis
│       ├── SKILL.md
│       ├── html2pptx.md             # HTML→PPTX workflow reference
│       ├── ooxml.md                 # PPTX OOXML editing reference
│       ├── html2pptx/{package.json,index.js}   # the html2pptx library
│       ├── ooxml/scripts/{unpack,pack,validate}.py
│       └── scripts/{inventory,replace,rearrange,thumbnail}.py
├── agents/                      # Subagents (invoke via the Agent tool)
│   ├── cpto-review.md            # Executive CPTO-level review
│   ├── prd-reviewer.md          # Senior-PM critique of a PRD/spec
│   ├── discovery-interviewer.md # Build/role-play/critique discovery interviews
│   ├── customer-brief-analyst.md# 1-page pre-meeting customer intel brief
│   ├── data-brief-analyst.md    # Insight brief from a provided dataset/file
│   ├── data-storyteller.md      # Narrative metrics brief (live Amplitude)
│   ├── market-research-analyst.md# Market sizing & competitive intelligence
│   ├── prototype-builder.md     # Zero-build interactive HTML prototypes
│   ├── ux-designer.md           # User flows, IA, and UX critique
│   └── voice-of-customer.md     # Synthesize customer signal into VoC themes
├── .gitignore
└── README.md
```

## Commands

| Command | What it does |
| --- | --- |
| `/prd [feature]` | Produces a structured PRD: problem, goals/non-goals, metrics, prioritized requirements, flows, milestones. |
| `/jtbd [product]` | Jobs-to-be-Done analysis: job statements, job map, forces of progress, outcome metrics, ranked opportunities. |
| `/discovery [idea]` | Discovery plan: riskiest assumptions, cheapest tests to invalidate them, and a non-leading interview guide. |
| `/add-mcp` | Reference for connecting MCP servers — claude.ai connectors and the `claude mcp add` CLI (scopes, examples, management). |
| `/competitive-analysis [competitor]` | Researches a competitor (via WebSearch) and produces a structured brief: positioning, feature & pricing comparison, sentiment, Porter's Five Forces, and recommended actions. |
| `/customer-brief [account]` | Runs the `customer-brief-analyst` agent to assemble a 1-page pre-meeting brief (usage, support sentiment, open issues, talking points) from Amplitude, Intercom, Glean, Jira, and Slack. |
| `/decision-brief [decision]` | Produces a crisp 1-page decision brief — options, trade-offs, and a clear recommendation. Runs the `decision-brief` skill. |

## Skills

These activate automatically when your request matches:

- **prd-writing** — triggers when you're turning an idea into a spec or tightening an existing PRD.
- **research-synthesis** — triggers when you have interview notes, surveys, or tickets to turn into ranked insights.
- **decision-brief** — produces a 1-page decision brief (framing, options, trade-off table, assumptions, and a clear recommendation with one next step). Backs the `/decision-brief` command.
- **churn-signal** — assesses churn/expansion risk for an account or segment: pulls usage + sentiment + engagement signals, scores account health (🟢/🟡/🟠/🔴), and recommends a specific intervention. Supports bulk segment mode.
- **debate** — stress-tests a product idea with parallel Champion vs Sceptic agents, then synthesises a risk register, minimum viable scope, assumption map, and a go/no-go recommendation.
- **design-an-interface** — "Design It Twice": spawns parallel sub-agents to produce radically different interface/API designs for a module, then compares them on simplicity, depth, and ease of correct use.
- **impact-sizing** — guides TAM/SAM/SOM + churn + opportunity analysis to translate a product hypothesis into an ARR estimate, then generates a multi-sheet Excel workbook (bundled `generate_impact_sizing.py`). Handles commercially sensitive CRM/churn data — anonymise and store securely.
- **interview-analysis** — analyses a folder of customer interview transcripts in parallel (Teresa Torres Continuous Discovery), extracting pain points, workflow use cases, terminology reactions, and unprompted signals, then synthesises cross-interview patterns. Includes analysis + synthesis templates; anonymises PII by default.
- **learn** — deep-dive research on a topic (web sources or a provided document), saved as a structured knowledge artifact in `~/.claude/knowledge/` for future reference. Keep saved knowledge general — not customer-specific data.
- **recall** — retrieves knowledge previously saved by `learn` (exact or fuzzy match across project/personal `knowledge/` dirs), or lists what's been learned. The read side of the learn/recall pair.
- **roadmap-narrative** — turns a rough roadmap into three audience-specific narratives (executive summary, engineering/team brief, customer-facing) off one input, after naming the narrative arc. Translates feature names into outcomes; never invents initiatives.
- **sprint-health** — pulls Jira sprint data (or a pasted board), checks velocity vs elapsed time, flags blockers/stale/scope-creep/unestimated issues, forecasts what slips, and emits a copy-paste status update (plus an end-of-sprint retro section).
- **parallel-prototype** — generates 3 structurally different HTML prototypes in parallel (wizard vs single-page vs dashboard, etc.), presents a comparison matrix, and optionally pushes the winner/all to Figma. Pairs with the prototype-builder agent.
- **rapid-prototype** — zero-build HTML prototyping kit: assembles interactive mockups from a bundled template + design system (tokenised Tailwind config), single-agent or parallel-agent workflow. Bundles `blank_prototype_template.html`, `DesignSystem.html`, and `CLAUDE.md` conventions.
- **pdf** — PDF manipulation toolkit: extract text/tables, create PDFs, merge/split, rotate, watermark, OCR scanned docs, and fill forms (via pypdf, pdfplumber, reportlab, and CLI tools like qpdf).
- **docx** — Word document creation, editing, and analysis: text extraction (pandoc), docx-js for new docs, OOXML editing, and a redlining workflow for precise tracked changes and comments.
- **pptx** — PowerPoint creation, editing, and analysis: text extraction (markitdown), html2pptx for new decks, template-based decks (rearrange/inventory/replace), OOXML editing, and thumbnail-grid visual validation.
- **web-browser** — remote-controls Chrome/Chromium via the Chrome DevTools Protocol (navigate, eval JS, screenshot, interactive element picker). Node tools built on `puppeteer-core` (run `npm install` in `tools/`; Node ≥18).
- **xlsx** — spreadsheet creation, editing, and analysis (openpyxl + pandas): formula-first construction, financial-model formatting conventions, zero-error delivery, and a LibreOffice-based `recalc.py` recalculation workflow.

## Agents

Invoke with the Agent tool (e.g. "have the prd-reviewer look at this"):

- **prd-reviewer** — critical, severity-ranked review of a PRD or proposal.
- **discovery-interviewer** — builds interview guides, role-plays customers, or critiques your questions (Mom Test style).
- **cpto-review** — brutally honest, commercially-aware executive review of PRDs, architectures, and strategic decisions from a CPTO perspective.
- **customer-brief-analyst** — assembles a 1-page pre-meeting intel brief on a named customer account by pulling live signals across your connected tools.
- **data-brief-analyst** — analyses a provided dataset (CSV, export, pasted table, or screenshot) and produces a structured insight brief with transparent calculations. Works from files, not live sources — use a live-analytics agent for Amplitude queries.
- **data-storyteller** — turns raw metrics, Amplitude data, or a dashboard into a narrative insight brief with "so what" framing (what happened → why → what it means). Calibrates to audience: exec brief, team review, or deep dive. Pairs with data-brief-analyst (files) by querying live Amplitude itself.
- **market-research-analyst** — senior-analyst market intelligence: market sizing (TAM/SAM/SOM with shown methodology), competitive landscape, customer segments, and strategic recommendations. Every figure carries an inline citation and a Data Sources section.
- **prototype-builder** — builds a self-contained, interactive HTML prototype from a PRD, brief, description, or Figma design. Zero-build (Tailwind CDN + vanilla JS), accessible, opens straight in a browser.
- **ux-designer** — UX direction for a feature: user flows, information architecture, interaction patterns, and design critique (Critical/Major/Minor). Thinks in journeys, not aesthetics — pairs with prototype-builder for the visual mockup.
- **voice-of-customer** — synthesises ambient customer signal (Intercom, Jira, Slack, Glean/Confluence, Amplitude, interview notes) into confidence-ranked insight themes with evidence and opportunity sizing. Produces a roadmap-ready VoC brief; anonymises accounts by default.

### customer-brief-analyst — features & how it works

A pre-call research assistant for PMs. Give it a customer account name (company and/or domain) and it returns a tight, scannable brief in under ~3 minutes, so you walk into a call or QBR already up to speed.

**What it pulls together**
- **Product usage (Amplitude)** — MAU/WAU, feature adoption, 90-day usage trend, and anomalies like sudden drop-offs or spikes.
- **Support & conversations (Intercom)** — the 5 most recent conversations, open/unresolved issues, recurring complaints, and direct pain-point quotes.
- **Internal knowledge (Glean)** — Slack threads, account/handover notes, CS call summaries, sales context, and past feedback sessions.
- **Open issues (Jira)** — tickets tagged to the account, linked feature requests, and commitments made to them.
- **Recent comms (Slack / Gmail)** — recent mentions and email threads where available.

**How it works**
1. Takes the account name as input.
2. Queries each source **in parallel**, and — importantly — **never blocks on a source that fails**; it skips it and records the gap instead.
3. Synthesises everything into a fixed 1-page template: Snapshot (tier, users, trend, 🟢/🟡/🔴 health) → What's Working → What's Broken → Open Commitments → Recent Activity → Talking Points → **Data Gaps** (so you know what's missing) with a sources footer.
4. Labels inferences explicitly ("Usage suggests…") and avoids padding — if there are only two talking points, it writes two.

> Requires the relevant connectors to be authorized (Amplitude, Intercom, Jira, Slack, etc. — via `/mcp`). Unauthorized or unavailable sources are reported under **Data Gaps** rather than causing a failure. This brief is internal prep for a meeting with the named customer, so it is not anonymised.

## Installing

### From GitHub (recommended)
Add the marketplace and install the plugin:

```
/plugin marketplace add sugirda-rgb/ai_toolkit
/plugin install ai-toolkit@ai-toolkit-marketplace
```

### Local development
Clone the repo and add it as a marketplace from the local path:

```bash
git clone https://github.com/sugirda-rgb/ai_toolkit.git
```

```
/plugin marketplace add ./ai_toolkit
/plugin install ai-toolkit@ai-toolkit-marketplace
```

Then restart or reload, and run `/help` to confirm the `/prd`, `/jtbd`, and `/discovery` commands appear. Agents show up under the Agent tool, and skills trigger automatically.

> Several agents rely on connectors (Amplitude, Intercom, Jira, Slack, Figma, etc.). Authorize these via `/mcp`; agents that pull live signals report unavailable sources as data gaps rather than failing.

## Development

- **Commands** are markdown files with YAML frontmatter (`description`, `argument-hint`). `$ARGUMENTS` is replaced with whatever the user types after the command.
- **Skills** live in `skills/<name>/SKILL.md` with `name` and `description` frontmatter. The description controls when Claude auto-triggers the skill, so keep it specific.
- **Agents** are markdown files with `name`, `description`, `tools`, and `model` frontmatter, followed by the system prompt.

After editing, bump `version` in `.claude-plugin/plugin.json` and reinstall.

## License

MIT © Sugirda Dinakar
