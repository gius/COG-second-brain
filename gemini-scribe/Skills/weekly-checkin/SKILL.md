---
name: weekly-checkin
description: Cross-domain pattern analysis and strategic reflection for weekly review
metadata:
  roles: all
  keywords: weekly checkin,weekly check-in,weekly review,reflect on my week,week reflection,weekly planning,end of week
  display-name: COG Weekly Checkin
---

# COG Weekly Check-in Skill

## Purpose
Comprehensive weekly review and analysis integrating insights across all domains (personal, professional, projects) with pattern recognition and strategic planning.

## When to Invoke
- User wants to do their weekly review
- User says "weekly checkin", "weekly review", "reflect on my week"
- End of week reflection time
- User wants to analyze patterns across the week

## Agent Mode Awareness

**Delegation buckets** (`agent_mode: team` only — mode check and tier rules in `AGENTS.md → Model Tiers`): at most 3 specialist-tier sub-agents, one per provenance bucket: (1) personal-domain scan, (2) professional-domain scan, (3) all-projects-combined scan. **Do NOT spawn one agent per active project** — each agent costs ~40K context overhead, and per-project context is rarely deep enough to need isolation. Skip any bucket with no fresh content in the window.

## Pre-Flight Check

**Check for user profile (optional but enhances experience):**

1. Look for `00-inbox/MY-PROFILE.md` in the vault
2. If found:
   - Read user's name for personalization
   - Read active projects to review project-specific progress
   - Tailor reflection questions to user's role and projects

**Vault operations and timestamp:** Read `.agents/skills/obsidian/SKILL.md` for vault I/O operations (file creation, search, properties, tags, tasks) and follow its timestamp rule and YAML formatting.

## Process Flow

### 1. Gather Context

Scan recent files from the past week:
- Daily briefs in `01-daily/briefs/`
- Braindumps in `02-personal/braindumps/`, `03-professional/braindumps/`, `04-projects/*/braindumps/`
- Previous check-ins in `01-daily/checkins/`
- Knowledge index `05-knowledge/_index.md` — note frameworks/patterns relevant to this week's themes (fallback if missing: scan `05-knowledge/consolidated/` and `05-knowledge/patterns/` directly)

If `MY-PROFILE.md` available:
- Use user's name for personalization
- Reference their active projects
- Tailor questions to their role

#### Knowledge Health Check

Assess consolidation debt:
- Count braindumps with `status: "captured"` across `02-personal/braindumps/`, `03-professional/braindumps/`, `04-projects/*/braindumps/`, and `00-inbox/braindump-*.md`
- Find the most recent `05-knowledge/consolidated/consolidation-*.md` and extract its date
- Calculate days since last consolidation
- **Read that consolidation report's content** (Major Themes, frameworks updated/created) — not just its date. Carry it into Pattern Recognition below so this week's reflection builds on the last synthesis instead of restarting from zero.

### 2. Guided Reflection

#### Evidence Pre-Fill

Before asking anything, draft from the files gathered in Step 1: per-domain activity summary, candidate wins/challenges, per-project progress (braindumps, briefs, PROJECT-OVERVIEW changes). Present drafts for correction instead of asking open questions the vault can already answer. Ask only what the evidence can't show: rating, corrections, energy/wellbeing, surprises, forward priorities.

Lead the user through the remaining questions in a warm, conversational tone — one message per block, not one per question:

#### Overall Week Assessment
Present the drafted wins/challenges, then **ask:**
- "How would you rate this week on a 1-5 scale? Why that rating?"
- "What did I miss or get wrong in this summary?"

**Listen for:**
- Overall sentiment and energy
- Key accomplishments they're proud of
- Obstacles they faced
- Emotional tone of the week

#### Domain Reviews

**Personal Domain:**
Present the drafted summary (often thin — vault evidence skews professional), then **ask:**
- "How were your energy levels and well-being — anything the vault can't show?"
- "Any personal growth or insights?"

**Professional Domain:**
Present the drafted summary, then **ask:**
- "Corrections? Any standout moments the files don't capture?"
- "Anything with team, colleagues, or learning worth recording?"

**Estimation Log Review (if `03-professional/ESTIMATION-LOG.md` exists):**
- Review the week's estimation entries
- Calculate average ratio for the week
- Ask: "Looking at your estimates vs actuals this week, what patterns do you notice?"
- Help identify common blind spots (testing? edge cases? scope creep?)
- Update the "My Calibration" section if enough data accumulated (~10+ tasks)
- If the file doesn't exist: skip silently; if the user brings up estimates or quoting during the review, offer to create it

**Projects Domain (if applicable):**
For each active project from MY-PROFILE.md, present the drafted progress (from PROJECT-OVERVIEW + braindumps), then **ask** only about gaps:
- "What's blocking you / what's not visible in the vault?"
- "Any direction changes?"

#### Pattern Recognition

Before asking, check this week's themes against the knowledge index (`05-knowledge/_index.md`): which documented patterns/frameworks does this week's evidence touch?

**Ask:**
- For themes matching a documented pattern: "This week looks like [[pattern-x]] again — does it confirm the pattern, or is something different this time?"
- For evidence cutting against a framework: "You documented [[framework-y]], but [this week's evidence] contradicts it — evolution or exception?"
- "Any connections between different areas of your life - personal, professional, projects?"
- "What surprised you this week?"

**Record:**
- Link canonical pattern/framework docs — never re-describe a documented pattern from scratch
- Recurring theme with no doc yet → mark as **candidate pattern** for the next consolidation
- Confirmed contradictions → append a line to the index's **Open Contradictions** section (only `/knowledge-consolidation` removes entries there)

#### Forward Planning

**Ask:**
- "What are your top 3 priorities for next week?"
- "Anything from this week you want to carry forward?"
- "What do you want to do differently next week?"
- "What success would look like next week?"

**Help with:**
- Clarifying priorities
- Being specific about goals
- Identifying experiments to try
- Setting measurable outcomes

### 3. Generate Weekly Check-in Document

Based on the conversation, create a structured check-in document:

```markdown
type: "weekly-checkin"
domain: "integrated"
date: "YYYY-MM-DD"
week_of: "YYYY-MM-DD"
created: "YYYY-MM-DD HH:MM"
tags: ["weekly-checkin", "reflection", "planning"]
domains_analyzed: ["personal", "professional", "projects"]
rating: [1-5]
braindumps_reviewed: [count]
briefs_reviewed: [count]
```

**Required sections, in this order.** Write them in the user's own language, at whatever length the week warrants. Do not pad a quiet week to fill headings, and do not force a section that has nothing behind it.

1. `# Weekly Check-in - Week of [Date]`
2. `## Executive Summary` — week rating 1-5 in the user's own reasoning, the week in three words, highlights, challenges.
3. `## Domain Reviews` — `### 💭 Personal`, `### 💼 Professional`, `### 🎯 Projects` (one `####` sub-section per active project). Each domain carries its own **Rating:** [1-5] ⭐. Professional includes an Estimation Calibration block when the user tracks it (tasks logged, average ratio, pattern noticed, current multiplier). Each project carries **Current Status** (`On track | Needs attention | Blocked | Pivoting`), blockers, and Next Steps as tasks.
4. `## 📚 Knowledge Health` — unconsolidated braindump count, last consolidation date and days since, debt level (`Low <10 | Medium 10-20 | High 20+ | Critical 30+`). At Medium or above, recommend `/knowledge-consolidation`.
5. `## 🔍 Pattern Recognition` — recurring themes, each linked to its canonical doc where one exists: `**[Theme]** ([[pattern-doc]] — confirms/extends | *candidate pattern, no doc yet*)`. Include a **Framework Check** only when the week's evidence actually touched a documented framework, listing Confirms and Contradicts; every Contradicts entry is also appended to `05-knowledge/_index.md` Open Contradictions. Then energy and productivity patterns, cross-domain connections, and how their thinking evolved.
6. `## 📅 Forward Planning` — top 3 priorities and why they matter, carry-forward items as tasks, experiments (try differently / keep doing / stop), and success criteria for next week.
7. `## 📊 Week in Review` — counts of braindumps, briefs and prior check-ins analyzed; most active domain; dominant themes; sentiment trend.
8. `## 💡 Insights & Notes` — strategic observations, questions worth deeper reflection, optional gratitude.

Close with `*Generated by COG Weekly Check-in Skill | Integrating insights across all domains*`.

All tasks use the emoji format with real dates: `- [ ] Action 📅 YYYY-MM-DD`. Next Steps default to next Monday / next Friday / +1 week; carry-forward items to next Monday / mid-next-week / +1 week.

Save to: `01-daily/checkins/weekly-checkin-YYYY-MM-DD.md`

### 4. Confirm Completion

After creating the check-in:
- Confirm file was created
- Show user: "Weekly check-in saved to [file path]"
- Highlight 1-2 key patterns spotted
- Offer to review patterns across multiple weeks if helpful
- Ask if they want to capture any follow-up thoughts via braindump skill

## Conversational Guidelines

### Do:
- Have a warm, empathetic, conversational tone
- Ask thoughtful follow-up questions based on user's answers
- Help identify patterns they might not see themselves
- Be honest and objective in summarizing their reflections
- Celebrate wins genuinely and specifically
- Acknowledge challenges without sugar-coating or minimizing
- Show curiosity about their experiences
- Reflect back what you're hearing for validation

### Don't:
- Rush through the questions
- Make assumptions about what matters to them
- Judge their answers or week rating
- Over-structure their free-form reflections
- Force positivity if they had a tough week
- Dismiss their challenges or concerns
- Skip the emotional/energy assessment
- Be clinical or robotic in tone

## After Completion

After saving the check-in, suggest:
- `/knowledge-consolidation` — if patterns across multiple weeks are ready for framework synthesis
- `/braindump` — if the reflection sparked new thoughts worth capturing separately
- Review patterns across multiple check-ins for long-term trends

## What Good Looks Like

A successful weekly check-in means: the user completed a meaningful reflection (not rushed), patterns across domains were identified and documented, clear priorities are set for next week with real dates, the user feels heard and understood, and cross-domain insights reveal connections the user might not have seen on their own.

