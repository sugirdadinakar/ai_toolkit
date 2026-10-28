---
name: prd-writing
description: Write and refine Product Requirements Documents (PRDs) and feature specs. Use when the user wants to turn a feature idea, problem statement, or user request into a structured spec — defining goals, non-goals, requirements, success metrics, and acceptance criteria, or breaking a large ask into a phased document.
---

# PRD Writing

Turn a problem or idea into a crisp, build-ready PRD. This skill guides the full flow from fuzzy input to a document engineers and designers can act on.

## When to use
- The user has a feature idea or problem and needs it written up as a spec/PRD.
- An existing PRD needs tightening, restructuring, or a missing section filled in.
- A big initiative needs to be broken into a phased, prioritized plan.

## Process

1. **Understand before writing.** Identify the user, the job-to-be-done, and the success metric. Ask at most 3 high-leverage clarifying questions. If the user wants speed, proceed on reasonable assumptions and list them explicitly.

2. **Draft the PRD** with these sections:
   - **Summary** — what, for whom, why now (one paragraph).
   - **Problem** — the user problem with evidence; frame as a job-to-be-done.
   - **Goals & non-goals** — bulleted; non-goals prevent scope creep.
   - **Success metrics** — one primary metric + 1–2 guardrails, with rough targets.
   - **Requirements** — user stories / functional requirements, prioritized P0/P1/P2.
   - **UX & flows** — key flows and edge cases.
   - **Open questions** — unresolved decisions and their owners.
   - **Milestones** — phased rollout (MVP → v1 → fast-follow).
   - **Assumptions** — anything inferred rather than confirmed.

3. **Pressure-test** before finishing:
   - Is every requirement traceable to the problem?
   - Could an engineer estimate this? If not, it's too vague.
   - Are non-goals explicit? Is the primary metric singular and measurable?

## Style
- Concrete over aspirational. "Cuts report generation from 5 min to 30 s," not "improves efficiency."
- No buzzwords or filler. Every sentence earns its place.
- When you make a tradeoff, state it and give the one-line rationale.

## Output
Save the PRD as a kebab-case markdown file in the project when working in a repo; otherwise return it inline. Offer to generate a companion `/jtbd` analysis or `/discovery` plan if value risk is still open.
