---
name: "cog-knowledge-consolidation"
displayName: "COG Knowledge Consolidation"
description: "Build frameworks from scattered insights, or run a lightweight vault health audit with freshness scoring and orphan detection"
keywords: ["consolidate knowledge", "build frameworks", "synthesize insights", "extract patterns", "knowledge consolidation", "create framework", "analyze patterns", "vault health", "vault audit", "vault status", "stale content", "orphan notes"]
---


# COG Knowledge Consolidation Skill

## Purpose
Transform scattered insights from braindumps, daily briefs, research, bookmarks, and all other vault content into coherent frameworks and "single source of truth" knowledge documents through pattern recognition and systematic synthesis. Optionally run in **audit-only** mode for a lightweight vault health check without full synthesis.

## When to Invoke
- User wants to consolidate their insights
- User says "consolidate knowledge", "build frameworks", "synthesize insights"
- Time for periodic knowledge base maintenance (weekly, monthly, quarterly)
- User wants to extract patterns from accumulated braindumps
- Before major decisions that could benefit from framework consultation
- User asks about vault health, stale content, or what needs attention ("vault audit", "vault health", "vault status", "what needs attention?")

## Invocation Modes

This skill supports two modes. Determine which mode from user intent:

### Full Consolidation (default)
The complete pipeline: scan → pattern recognition → framework synthesis → cleanup. Use when the user says "consolidate", "build frameworks", "synthesize", or doesn't specify a mode.

### Audit Only (lightweight)
A quick vault health report without framework synthesis. Use when the user says "vault health", "vault audit", "vault status", "what needs attention", or explicitly asks for an audit without consolidation.

**Audit-only skips:** Steps 2 (Pattern Recognition), 3 (Framework Development), and 4 (Knowledge Integration). It runs Step 1 (Data Gathering) with expanded statistics, the Freshness & Decay Assessment, and generates a Vault Health Report instead of the full consolidation report.

## Agent Mode Awareness

**Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:**
- If `agent_mode: team` — delegate scanning and pattern extraction to parallel sub-agents (e.g., one per domain: personal braindumps, professional braindumps, project-specific content, daily briefs). Each agent identifies themes and patterns, then a synthesis agent combines findings into frameworks.
- If `agent_mode: solo` (default) — handle all scanning, pattern recognition, and framework building directly. No delegation.

## Pre-Flight Check

**Get current timestamp (REQUIRED before generating any files):**

1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
2. Store this value and use it for the `created:` frontmatter field
3. NEVER guess or fabricate the time — always use the value returned by the `date` command

## Depth Scaling

The scope the user chooses determines how deep to go. Not every run should produce the same artifacts — a weekly pass over 5 braindumps shouldn't create new frameworks or timeline entries.

| Scope | Focus | Create new frameworks? | Create timeline entries? | Create patterns? |
|---|---|---|---|---|
| **Weekly** (< ~15 docs) | Update existing frameworks with new evidence. Flag emerging themes for future runs. | No — only update existing | No | Only if frequency ≥ 3 mentions |
| **Monthly** (~15-60 docs) | Full pattern recognition. Create new frameworks if evidence is strong (≥ 5 supporting sources). | Yes, if well-evidenced | Yes, for clear thinking shifts | Yes |
| **Quarterly / All time** (60+ docs) | Deep synthesis. Create frameworks, timelines, and cross-domain patterns. Challenge and retire stale frameworks. | Yes | Yes | Yes |

When in doubt, err toward lighter output. A framework created too early from thin evidence wastes more effort than one created a month later from solid evidence.

## Process Flow

### 1. Data Gathering

**Scan vault for ALL content (not just braindumps).** Each content type has different characteristics — the processing notes below explain what to extract vs. skip during pattern recognition (Step 2).

- **Braindumps** (all domains):
  - `02-personal/braindumps/`
  - `03-professional/braindumps/`
  - `04-projects/*/braindumps/`
  - `00-inbox/braindump-*.md` (mixed domain)
  - **Processing note:** Primary raw material. Extract themes, decisions, recurring questions, and emotional patterns. These are the user's unfiltered thinking — treat every braindump as potentially containing framework-worthy insights.

- **Daily & team intelligence:**
  - `01-daily/briefs/` (daily briefs AND team briefs)
  - `01-daily/checkins/` (weekly check-ins)
  - **Processing note:** Briefs are curated snapshots, not raw thinking. Extract strategic implications and action item patterns. Weekly check-ins are particularly valuable — they contain the user's own reflections on what matters. Skip news summaries that are purely informational.

- **Strategic research:**
  - `05-knowledge/research/` (auto-research output)
  - **Processing note:** Research contains synthesized findings and scenarios. Extract conclusions, recommended actions, and how they relate to existing frameworks. Research that contradicts current frameworks is especially important — flag it for contradiction analysis.

- **URL bookmarks & booklets** (tools, articles, references saved via url-dump):
  - `05-knowledge/booklets/` (all categories)
  - **Processing note:** Booklets are reference material, not raw thinking. Extract only:
    - Strategic relevance from "Why This Matters" / "Why It's Relevant" sections
    - Cross-references and patterns across multiple booklets (e.g., clustering of tool evaluations reveals strategic priorities)
    - Connections to braindumps and project goals
    - Skip tool feature descriptions and technical specs — those are documentation, not insight

- **Project artifacts:**
  - `04-projects/*/planning/` (meeting transcripts, planning docs)
  - `04-projects/*/resources/` (project resources)
  - `04-projects/*/PRDs/` (product requirements)
  - `04-projects/*/releases/` (release notes)
  - `04-projects/*/stories/` (user stories)
  - `04-projects/*/audits/` (issue audits)
  - **Processing note:** Different artifact types serve different purposes:
    - *Meeting notes* — extract decisions made, action items, and recurring blockers. Decision patterns across meetings are high-value.
    - *PRDs* — extract product direction, scope decisions, and trade-offs. Useful for tracking how product thinking evolves.
    - *Release notes* — extract shipping cadence and feature evolution patterns. Individual releases are low-value; trends across releases are high-value.
    - *Stories & audits* — mostly skip for consolidation unless they reveal recurring themes (e.g., same type of bug keeps appearing).

- **Competitive intelligence:**
  - `04-projects/*/competitive/` (per-project competitive intel)
  - `03-professional/COMPETITIVE-WATCHLIST.md`
  - **Processing note:** Extract competitor strategy trends and market position shifts. Individual data points matter less than trajectories — is a competitor consistently moving in a direction? Cross-reference with braindumps where the user reacted to competitive moves.

- **Existing knowledge base** (for staleness check):
  - `05-knowledge/consolidated/` (frameworks)
  - `05-knowledge/patterns/` (patterns)
  - `05-knowledge/timeline/` (timeline entries)

**Determine scope:**
- Ask user: "What time period should I analyze? (last week, last month, last quarter, all time, or custom range?)"
- If audit-only mode: default to "all time" without asking
- Map the chosen scope to the depth scaling table above
- Identify unprocessed content (check for `status: "captured"` or missing consolidation metadata)

**Gather statistics:**
- Total documents by content type (braindumps, briefs, research, bookmarks, PRDs, release notes, competitive intel, etc.)
- Breakdown by domain and project
- Date range coverage
- Unprocessed vs. consolidated counts
- Oldest unprocessed document age

### 1b. Freshness & Decay Assessment

**Run in both modes (full consolidation and audit-only).**

Score each document on freshness using category-weighted decay. Content types that represent decisions and strategic thinking decay slower than transient data.

#### Category Weights

| Category | Weight | Decay Threshold | Examples |
|----------|--------|-----------------|----------|
| Frameworks & patterns | 1.5x | 90 days | `05-knowledge/consolidated/`, `05-knowledge/patterns/` |
| Decisions & PRDs | 1.3x | 60 days | `04-projects/*/PRDs/`, meeting decisions |
| Strategic research | 1.2x | 45 days | `05-knowledge/research/` |
| Braindumps | 1.0x | 30 days | All braindump locations |
| Bookmarks & URLs | 1.0x | 60 days | `05-knowledge/booklets/` |
| Release notes & audits | 0.8x | 90 days | `04-projects/*/releases/`, `04-projects/*/audits/` |
| Daily briefs & news | 0.5x | 14 days | `01-daily/briefs/` |

**Decay threshold** = the age after which content is flagged as potentially stale (needs review, not necessarily outdated). Use the `created:` or `last_updated:` frontmatter date, falling back to file modification time.

#### Connectivity Check

For each document, assess:
- **Inlinks:** How many other vault files reference this document? (search for `[[filename]]` patterns)
- **Outlinks:** How many wiki-links does this document contain?
- **Orphans:** Documents with zero inlinks AND zero outlinks (excluding profile/config files in `00-inbox/`)
- **Dead links:** Wiki-links pointing to files that don't exist

**Performance guidance:** A full connectivity check is O(n²) — every file searched for every other filename. Scale the approach to vault size:
- **Small vaults (< 100 docs):** Full check is fine.
- **Medium vaults (100-500 docs):** Batch the search — collect all filenames first, then search for all of them in a single pass per file using grep with multiple patterns.
- **Large vaults (500+ docs):** In solo mode, sample the top 50 oldest/most-connected documents rather than checking every file. In team mode, delegate to a sub-agent that can run the full check in the background.
- **Audit-only mode:** Always acceptable to sample rather than exhaustively check. Report the sample size.

#### Health Scoring (per document)

Score each document 0-100 across four dimensions:
- **Completeness (30%):** Has frontmatter? Has required fields for its type? Non-empty body?
- **Connectivity (30%):** Inlink count + outlink count relative to vault average
- **Metadata quality (20%):** Valid frontmatter fields, consistent tagging, proper date formats
- **Freshness (20%):** Age relative to category decay threshold, weighted by category

**Vault health score** = weighted average of all document scores, reported as a single 0-100 number.

### 2. Pattern Recognition

**(Skip this step in audit-only mode.)**

Apply systematic pattern detection across all content, using the processing notes from Step 1 to weight each content type appropriately:

#### Frequency Analysis
**What comes up repeatedly?**
- Identify themes mentioned across multiple documents
- Track topic frequency and clustering
- Recognize persistent questions or concerns
- Spot recurring action items or decisions

#### Temporal Clustering
**What insights emerged together?**
- Group related insights by time period
- Identify how thinking evolved over time
- Recognize inflection points where thinking shifted
- Map catalysts that triggered changes

#### Domain Correlation
**What patterns cross domains?**
- Personal insights affecting professional thinking
- Professional learnings applied to projects
- Project experiences informing personal growth
- Strategic themes spanning all domains

#### Contradiction Analysis
**Where does thinking conflict?**
- Identify contradictory thoughts or approaches
- Recognize evolution vs. inconsistency
- Understand resolution or ongoing tension
- Track perspective shifts over time

#### Cross-Cutting Patterns
**Meta-patterns across all dimensions:**
- Decision-making approaches
- Problem-solving strategies
- Learning patterns
- Energy and emotional patterns
- Creative processes

### 3. Framework Development

**(Skip this step in audit-only mode.)**

Synthesize patterns into actionable frameworks. Respect the depth scaling table — for weekly scope, update existing frameworks only.

1. **Identify Core Principles** — What patterns reveal deeper truths? What rules or heuristics emerge?
2. **Test Against Evidence** — Do source insights support these principles? Are there counter-examples? What's the confidence level?
3. **Define Boundaries** — When does this framework apply vs. not apply? What assumptions does it rely on?
4. **Create Applications** — Specific use cases, decision-making applications, practical implementation steps.

### 4. Knowledge Integration

**(Skip this step in audit-only mode.)**

Update and create knowledge base documents using the templates below.

#### Framework Document

Save to: `05-knowledge/consolidated/[framework-name]-framework.md`

**Frontmatter fields:** `type: "consolidated-knowledge"`, `domain`, `framework`, `created`, `last_updated`, `consolidation_id`, `source_documents` (count), `status` (stable|working|emerging), `tags`

**Required sections:**
- **Framework Overview** — What it is, current status, source count
- **Core Principles** — Each principle gets: clear statement, evidence (linked sources `[[doc]]`), how it evolved, confidence level (High/Medium/Low with reasoning)
- **Applications & Use Cases** — When to apply, how to apply (steps), expected outcomes, real examples from the user's experience
- **Boundaries & Limitations** — Works when / doesn't work when / common pitfalls
- **Evolution & History** — Chronological development: what emerged, what catalysts triggered it, evidence trail per phase. End with "Current State" showing latest understanding.
- **Related Frameworks** — Links to other frameworks with relationship descriptions
- **Future Development** — Questions to explore, potential extensions, signals to watch for

For **new frameworks**, set `status: "emerging"` and note that it needs more evidence and validation.

#### Pattern Document

Save to: `05-knowledge/patterns/pattern-[name].md`

**Frontmatter fields:** `type: "pattern-analysis"`, `pattern`, `created`, `domains` (array), `frequency` (high|medium|low), `tags`

**Required sections:**
- **Pattern Description** — What it is, frequency, which domains, why it matters
- **Occurrences** — For each: date, source document link, context, how the pattern manifested, outcome
- **Analysis** — What triggers this pattern, what follows it, cross-domain implications, potential actions (amplify if positive, mitigate if negative)
- **Evolution Over Time** — How the pattern has changed or stayed consistent

#### Timeline Entry

Save to: `05-knowledge/timeline/[topic]-evolution-YYYY-MM.md`

Only create for quarterly+ scope or when a clear thinking shift is identified across multiple documents.

**Frontmatter fields:** `type: "timeline-entry"`, `topic`, `date_range`, `created`, `tags`

**Required sections:**
- **What Changed** — Initial state → end state, the fundamental shift
- **Catalysts & Triggers** — Dated events with source links and impact descriptions
- **Evidence Trail** — Chronological: early thinking → intermediate development → current understanding, each with linked sources
- **Impact** — How this shift affects decisions, strategies, frameworks, and actions
- **Lessons Learned** — What this evolution teaches, future implications

### 5. Generate Consolidation Report

Save to: `05-knowledge/consolidated/consolidation-YYYY-MM-DD.md`

**Frontmatter fields:** `type: "knowledge-consolidation"`, `domain: "integrated"`, `date`, `consolidation_period`, `created` (with HH:MM), `sources_analyzed`, `frameworks_updated` (array), `frameworks_created` (array), `patterns_identified` (count), `tags`

**Required sections:**
- **Executive Summary** — Period analyzed, document counts by type (braindumps, briefs, check-ins, research, bookmarks, project docs, competitive intel, meeting notes), major outcomes (frameworks updated/created, patterns identified, timeline entries), top 3 key insights synthesized
- **Major Themes This Period** — For each: frequency, evolution, key insights with source links, framework implications, status (stable understanding | still exploring | needs more evidence)
- **Frameworks Updated** — For each: location link, what changed, new evidence added, confidence change (before → after), new applications
- **New Frameworks Created** — For each: location link, what prompted creation, core principles summary, primary use cases, status (emerging), what's needed to mature it
- **Patterns Identified** — For each: frequency, domains, description, implications, link to pattern doc
- **Thinking Evolution** — Major shifts with timeline, catalysts, impact, link to timeline doc
- **Cross-Cutting Insights** — Cross-domain connections, contradictions identified (with resolution status), strategic implications
- **Knowledge Base Maintenance** — Updates made checklist, archive actions (braindumps marked consolidated, superseded content archived)
- **Future Consolidation Needs** — Ready for framework creation, needs deeper analysis, monitoring required — each with target dates using `📅 YYYY-MM-DD`
- **Quality Assessment** — Completeness, coherence, traceability, actionability, evolution documented

### 5b. Generate Vault Health Report (audit-only mode)

**Use this instead of Step 5 when running in audit-only mode.**

Save to: `05-knowledge/consolidated/vault-health-YYYY-MM-DD.md`

**Frontmatter fields:** `type: "vault-health-audit"`, `domain: "integrated"`, `date`, `created` (with HH:MM), `vault_health_score` (0-100), `total_documents`, `tags`

**Required sections:**
- **Overall Health Score: [X]/100** — Table with dimensional breakdown (Completeness, Connectivity, Metadata Quality, Freshness) — each with score and notes
- **Content Inventory** — Table: content type | count | unprocessed | oldest unprocessed | avg age. Include all types (braindumps by domain, daily/team briefs, check-ins, research, bookmarks, PRDs, releases, stories, audits, competitive intel, meeting notes, frameworks, patterns, timeline entries). End with totals row.
- **Freshness Report** — Stale content table (document, type, age, threshold, action needed). Frameworks needing evidence (status emerging/working, last updated, days since update).
- **Connectivity Report** — Orphaned documents list (path, type, created date). Dead links list (broken reference, source file). Most connected hub documents table (top 5 by inlink + outlink count).
- **Recommended Actions** — Three tiers: Immediate (this session), Next Consolidation, Maintenance. Each with specific actionable items.

**Interpretation guide for the score:**
- 90-100: Excellent — vault is well-maintained
- 70-89: Good — some attention needed
- 50-69: Fair — significant maintenance backlog
- Below 50: Needs attention — run full consolidation

After generating, present the user with:
- The overall health score and a one-line assessment
- Top 3 most urgent recommended actions
- Offer to run full consolidation if unprocessed backlog is significant

### 6. Cleanup and Archival

**Mark processed braindumps:**
Update frontmatter in processed braindumps:
```yaml
status: "consolidated"
consolidated_in: "[[consolidation-YYYY-MM-DD]]"
consolidated_date: "YYYY-MM-DD"
```

**Archive outdated content:**
Move superseded frameworks or insights to:
`00-inbox/archive/[filename]-archived-YYYY-MM-DD.md`

Add note explaining why archived and what supersedes it.

**Maintain clean knowledge base:**
- Remove redundancy while preserving important context
- Update cross-references
- Fix broken links
- Ensure consistent tagging

### 7. Confirm Completion

After consolidation:
- Show user: "Knowledge consolidation complete! Processed [X] documents"
- Highlight: "[X] frameworks updated, [X] new frameworks created"
- Show: "Consolidation report saved to [file path]"
- Suggest reviewing key frameworks created/updated
- Offer to explain any specific framework in detail

## Consolidation Guidelines

### Quality Over Quantity
- Don't force insights that aren't mature enough
- Let patterns emerge naturally from evidence
- Mark frameworks as "emerging" vs "working" vs "stable"
- A framework created too early from thin evidence wastes more effort than one created later with solid evidence

### Preserve Nuance
- Don't over-simplify complex insights
- Maintain important context and conditions
- Preserve contradictions that haven't resolved yet
- Acknowledge uncertainty explicitly

### Maintain Traceability
- Always link back to source documents with `[[wiki-links]]`
- Show evidence trail for framework claims
- Document evolution of thinking
- Make it easy to audit and revise frameworks later

### Living Documents
- Frameworks should evolve with new insights
- Regular updates better than perfect first draft
- Clear status indicators (emerging/working/stable)
- Version history through Git
