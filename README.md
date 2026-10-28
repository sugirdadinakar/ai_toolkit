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
