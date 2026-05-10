
# COG Daily Brief Skill

## Purpose
Find verified, relevant news for personalized daily briefings with strict verification standards and strategic relevance analysis tailored to user's specific interests and projects.

## When to Invoke
- User wants their daily news briefing
- User says "daily brief", "news", "what's happening", "morning brief"
- User wants to stay updated on their interests
- Morning routine or regular check-in time

## Agent Mode Awareness

**Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:**
- If `agent_mode: team` — delegate news research to **specialist-tier** sub-agents grouped by topic cluster (≤4 agents). One agent per topic cluster, NOT one per news source. Each agent searches, verifies primary sources, and returns findings with `Verification proof`. Combine and synthesize in main context.
- If `agent_mode: solo` (default) — handle all research and synthesis directly. No delegation.

## Interest Tiers

Topics in `MY-INTERESTS.md` may be annotated `[weekly]`. These are slower-moving topics that don't need daily coverage.

- **No annotation** — search every run.
- **`[weekly]`** — search on the **first brief of the current ISO week** (Monday 00:00 → Sunday 23:59), or when the user explicitly requests full brief coverage. Skip silently otherwise.

**Implementation:** Check the most recent brief's filename date (from the dedup scan in Step 1). If it's before Monday of the current ISO week (or no previous brief exists), this run qualifies as "first of the week."

## Pre-Flight Check

**Before executing, check for user profile:**

1. Look for `00-inbox/MY-PROFILE.md` and `00-inbox/MY-INTERESTS.md` in the vault
2. If NOT found:
   ```
   Welcome to COG! Daily briefs work best when personalized.

   Let's quickly set up your profile (takes 2 minutes).

   Would you like to run onboarding first, or should I generate a general brief?
   ```
3. If found:
   - Read `MY-INTERESTS.md` to get topics for news curation
   - Read `MY-PROFILE.md` to get user's name and active projects
   - Read `03-professional/COMPETITIVE-WATCHLIST.md` if exists for competitive tracking
   - Use topics to curate relevant news
   - Connect news to user's active projects when relevant

**Vault operations and timestamp:** Read `.agents/skills/obsidian/SKILL.md` for vault I/O operations (file creation, search, properties, tags) and follow its timestamp rule and YAML formatting.

## Process Flow

### 1. Gather Context

Collect the information needed for personalized curation:

- Read `00-inbox/MY-PROFILE.md` for user's name, role, active projects
- Read `00-inbox/MY-INTERESTS.md` for topics and preferred news sources
- Read `03-professional/COMPETITIVE-WATCHLIST.md` (if exists) for companies/people to track

#### Deduplication — Previous Brief Scan

Read up to 3 most recent daily briefs from `01-daily/briefs/` (most recent first):
- Extract `dedup_urls` from their frontmatter (if present)
- Also scan their headlines/story titles as semantic fallback for cross-source matching
- Build a set of **covered stories** to avoid repeating

**Matching rules (in priority order):**
1. **URL match (primary):** If a candidate story's main source URL already appears in `dedup_urls`, it's a known story
2. **Headline match (fallback):** If the URL is different but the headline describes the same event as a previous story, treat as duplicate — this catches the same story reported by different outlets

During news research (Step 2), apply dedup rules:
- **Skip** stories already covered unless there is a **material update** (new data, resolution, escalation, reversal)
- If including an update, prefix with "**Update:** _first covered [date]_"
- Stories older than 3 briefs are eligible for re-inclusion if still developing

### 2. News Research and Curation

#### Interest-Based Research
- Search based on user's current interest profile
- Focus on strategic relevance to user's role and projects
- Identify emerging patterns and developments
- Diversify sources for balanced perspective

#### Verification

Source verification follows the research delegation rules in `AGENTS.md → Briefing sub-agents`. Apply them to news specifically:

- **Primary sources for news:** the original publisher (first outlet to break the story), official company/vendor announcements, GitHub releases pages, GHSA/CVE entries, government or regulatory notices. Aggregators (newsletters, Medium, "top X" roundups, release-tracking sites) are discovery paths, not primary sources — chase them back to the primary and cite that.
- **One authoritative primary source is enough.** Do not demand a second source when the first is the project's own official channel. Two sources matter only when the primary is disputed.
- **All news must fall within the last 7 days.** If a sub-agent returns an item outside the window, drop it or clearly mark it as context with the actual date shown inline.
- **Sub-agent return format must include a `Verification proof` field** with the WebFetched title and publication date. Items without this field are dropped before synthesis — no "medium confidence" laundering.

#### Strategic Relevance Analysis

Assess impact on user at three levels:

- **Direct Impact (High Priority):** News directly affecting user's projects, regulatory changes in their industry, competitive moves by direct competitors, tech developments affecting their stack
- **Strategic Impact (Medium):** Market trends affecting target customers, investment patterns, talent market changes, partnership opportunities
- **Contextual Impact (Lower):** Broader economic trends, future-oriented technology trends, industry thought leadership

#### Opportunity and Threat Identification

Scan for actionable signals:
- **Opportunities:** New markets opening, tools to leverage, partnership candidates, competitor weaknesses
- **Threats:** New competitors, disruptive tech, market shifts, regulatory changes

### 3. Generate Daily Brief

Save to: `01-daily/briefs/daily-brief-YYYY-MM-DD.md`

**Frontmatter fields:** `type: "daily-brief"`, `domain: "shared"`, `date`, `created` (with HH:MM), `sources_verified: true`, `news_age_verified: true`, `confidence`, `tags`, `interests` (array), `projects_referenced` (array), `items_count`, `dedup_urls` (array of primary source URLs for each story covered)

**Output sections** — use only the ones with real content this week. Don't pad empty buckets; a short brief with airtight items beats a long brief with filler.
- **Executive Summary** — 2-3 sentences highlighting the most important developments across all interest areas
- **High Impact News** — Stories with direct impact on user's projects/role. Each item gets: relevance explanation, summary, impact assessment (projects affected, potential effects, suggested action), primary source link
- **Strategic Developments** — Medium-priority strategic news with strategic implications
- **Market Intelligence / Technology Watch / Competitive Landscape** — optional sub-buckets if content warrants; merge or omit when thin
- **Opportunities & Recommendations** — Action items in Obsidian Tasks format (`📅 YYYY-MM-DD`): immediate actions (today/this week), research needed, people to inform/consult
- **Risks & Threats** — Active threats with mitigation approaches, emerging risks to monitor
- **Complete Sources** — Full citations grouped by section, with links

### 4. Handle Special Cases

**When No Recent News Found** for an interest area:
- State clearly: "No significant news found in last 7 days"
- Note last significant development if known
- Suggest expanding search criteria or alternative sources
- NEVER fabricate or use older news without explicit date disclosure

**When a claim cannot be verified against a primary source:** drop it. Do not include with a warning icon and a softened confidence label — that's how unverified content ends up shaping decisions.

**When two primary sources disagree:** present both with their URLs and note the disagreement explicitly. Do not pick a winner; let the user see the conflict.

### 5. Confirm Completion
- Confirm file was created
- Show user: "Daily brief saved to [file path]"
- Optionally show executive summary
- Ask if they want to explore any topic deeper or capture thoughts via braindump skill

## What Good Looks Like

A successful daily brief means: every item traces to a primary source the agent actually fetched, all news is within the 7-day window, the brief is relevant to the user's actual interests and projects, and opportunities/risks are actionable — not generic. The user should be able to forward any item to a colleague without saying "let me verify this first."
