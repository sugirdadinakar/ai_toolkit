# ai-toolkit

The Ultimate PM Toolkit for Claude Code — product-management commands, skills, and agents that help you go from fuzzy idea to build-ready spec.

## What's inside

```
ai-toolkit/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/                    # Slash commands (you invoke these)
│   ├── prd.md                   # /prd      — draft a PRD from a problem/idea
│   ├── jtbd.md                  # /jtbd     — Jobs-to-be-Done analysis
│   └── discovery.md             # /discovery — discovery plan + interview guide
├── skills/                      # Skills (auto-trigger from context)
│   ├── prd-writing/SKILL.md     # Writing and refining PRDs
│   └── research-synthesis/SKILL.md  # Synthesizing user research into insights
├── agents/                      # Subagents (invoke via the Agent tool)
│   ├── prd-reviewer.md          # Senior-PM critique of a PRD/spec
│   └── discovery-interviewer.md # Build/role-play/critique discovery interviews
└── README.md
```

## Commands

| Command | What it does |
| --- | --- |
| `/prd [feature]` | Produces a structured PRD: problem, goals/non-goals, metrics, prioritized requirements, flows, milestones. |
| `/jtbd [product]` | Jobs-to-be-Done analysis: job statements, job map, forces of progress, outcome metrics, ranked opportunities. |
| `/discovery [idea]` | Discovery plan: riskiest assumptions, cheapest tests to invalidate them, and a non-leading interview guide. |

## Skills

These activate automatically when your request matches:

- **prd-writing** — triggers when you're turning an idea into a spec or tightening an existing PRD.
- **research-synthesis** — triggers when you have interview notes, surveys, or tickets to turn into ranked insights.

## Agents

Invoke with the Agent tool (e.g. "have the prd-reviewer look at this"):

- **prd-reviewer** — critical, severity-ranked review of a PRD or proposal.
- **discovery-interviewer** — builds interview guides, role-plays customers, or critiques your questions (Mom Test style).
- **cpto-review** — brutally honest, commercially-aware executive review of PRDs, architectures, and strategic decisions from a CPTO perspective.
- **customer-brief-analyst** — assembles a 1-page pre-meeting intel brief on a named customer account by pulling live signals across your connected tools.
- **data-brief-analyst** — analyses a provided dataset (CSV, export, pasted table, or screenshot) and produces a structured insight brief with transparent calculations. Works from files, not live sources — use a live-analytics agent for Amplitude queries.

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

### From a marketplace (recommended)
If this repo is published as a plugin marketplace, add it and install:

```
/plugin marketplace add sugirda-rgb/ai_toolkit
/plugin install ai-toolkit
```

### Local development
Point Claude Code at a local marketplace that references this directory, or clone the repo and add it as a marketplace from the local path:

```bash
git clone https://github.com/sugirda-rgb/ai_toolkit.git
```

```
/plugin marketplace add ./ai_toolkit
/plugin install ai-toolkit
```

Then restart or reload, and run `/help` to confirm the `/prd`, `/jtbd`, and `/discovery` commands appear.

## Development

- **Commands** are markdown files with YAML frontmatter (`description`, `argument-hint`). `$ARGUMENTS` is replaced with whatever the user types after the command.
- **Skills** live in `skills/<name>/SKILL.md` with `name` and `description` frontmatter. The description controls when Claude auto-triggers the skill, so keep it specific.
- **Agents** are markdown files with `name`, `description`, `tools`, and `model` frontmatter, followed by the system prompt.

After editing, bump `version` in `.claude-plugin/plugin.json` and reinstall.

## License

MIT © Sugirda Dinakar
