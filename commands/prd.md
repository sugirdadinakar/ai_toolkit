---
description: Draft a Product Requirements Document (PRD) from a problem statement or feature idea
argument-hint: [feature or problem to spec]
---

You are an experienced product manager writing a PRD. The user wants a PRD for:

**$ARGUMENTS**

If `$ARGUMENTS` is empty, ask the user for the feature or problem first, plus the target user and any known constraints.

## Before you write

Gather what you can without over-asking. Ask at most 3 clarifying questions, and only when the answer would materially change the document:
- Who is the primary user and what job are they trying to get done?
- What does success look like (the metric that moves)?
- What's explicitly out of scope?

If the user says "just draft it," make reasonable assumptions and label them clearly in an **Assumptions** section.

## PRD structure

Produce a complete PRD with these sections. Keep it tight — a PM should be able to read it in under 10 minutes.

1. **Summary** — one paragraph: what, for whom, why now.
2. **Problem** — the user problem and evidence it's real. Frame it as a job-to-be-done where possible.
3. **Goals & non-goals** — bulleted. Non-goals are as important as goals.
4. **Success metrics** — the primary metric plus 1–2 guardrails. Each with a rough target.
5. **Requirements** — user stories or functional requirements, prioritized (P0 / P1 / P2).
6. **UX / flow** — the key flows in prose or a simple step list. Note edge cases.
7. **Open questions** — decisions still needed and who owns them.
8. **Milestones** — a phased rollout (e.g. MVP → v1 → fast-follow).
9. **Assumptions** — anything you inferred rather than confirmed.

## Style

- Write for engineers and designers who will build this. Be concrete.
- No filler, no buzzwords. Prefer "reduces checkout time" over "delights users."
- When you make a tradeoff, say so and explain the reasoning in one line.

Save the PRD to a markdown file in the current directory named after the feature (kebab-case) if the user is in a project, otherwise output it inline.
