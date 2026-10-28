---
name: recall
description: Retrieve previously saved knowledge from the knowledge base. Use to look up a topic you researched earlier with the learn skill, or to list what you've learned.
---

# Recall Skill

Retrieve knowledge artifacts saved by the [`learn`](../learn/SKILL.md) skill. This is the read side of the learn/recall pair.

## Input: $ARGUMENTS

Accepts:
- `/recall [topic]` — Retrieve knowledge on a specific topic (e.g., "React Server Components")
- `/recall` — List all saved knowledge files so the user can pick one

## Where knowledge lives

Knowledge files are markdown, saved by the `learn` skill. Search both scopes, most specific first:

1. **Project**: `.claude/knowledge/*.md` (if working inside a project)
2. **Personal**: `~/.claude/knowledge/*.md`

## Process

### Mode A: List (no topic given)
Enumerate available knowledge and show a short index:

```bash
ls -1 ~/.claude/knowledge/*.md 2>/dev/null
ls -1 .claude/knowledge/*.md 2>/dev/null   # if in a project
```

Present each as: `topic-name` + the `> Learned:` date + the TL;DR line (read the first few lines of each file). Ask which one to open.

### Mode B: Retrieve (topic given)
1. **Convert topic to kebab-case** the same way `learn` does (e.g., "React Server Components" → `react-server-components`).
2. **Look for an exact filename match** first:
   ```bash
   cat ~/.claude/knowledge/react-server-components.md 2>/dev/null \
     || cat .claude/knowledge/react-server-components.md 2>/dev/null
   ```
3. **If no exact match, fuzzy-search** filenames and contents:
   ```bash
   grep -ril "<topic keywords>" ~/.claude/knowledge/ .claude/knowledge/ 2>/dev/null
   ```
   - One match → open it.
   - Several matches → list them and ask which to open.
   - No match → say so, and offer to research it now with `/learn [topic]`.

## Output

When a knowledge file is found:
1. Present its contents (it's already structured: TL;DR, Core Concepts, Best Practices, etc.).
2. Lead with the **TL;DR** so the user gets the answer fast, then the detail.
3. Note the `> Learned:` date and sources so the user can judge freshness.
4. If the knowledge looks stale (old date, fast-moving topic), suggest refreshing it with `/learn [topic]`.

## Principles

- **Don't invent knowledge.** Only return what's actually in the knowledge base. If nothing matches, say so — don't answer from memory and present it as "recalled."
- **Freshness matters.** Always surface when the knowledge was learned; flag likely-stale entries.
- **Point back to learn.** When recall comes up empty, the natural next step is `/learn [topic]` to create the entry.
- **Respect scope.** Prefer project-scoped knowledge over personal when both exist for the same topic.
