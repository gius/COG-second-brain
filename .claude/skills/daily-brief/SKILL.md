---
name: daily-brief
description: Generate personalized news intelligence with verified sources (7-day freshness requirement)
metadata:
  roles: all
  integrations: web-search
  keywords: daily brief,news,what's happening,morning brief,daily news,intelligence briefing,news update,morning update
  display-name: COG Daily Brief
---

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
- If `agent_mode: team` — delegate news research across different interest areas to parallel sub-agents (e.g., one agent per topic cluster). Each agent searches, verifies sources, and returns findings. Combine and synthesize results into the final brief.
- If `agent_mode: solo` (default) — handle all research and synthesis directly in the conversation. No delegation.

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

#### Verification Standards (MANDATORY)

**Date Verification:**
- ALL news MUST be from last 7 days ONLY
- Verify publication dates with verified timestamps
- NEVER include older news without explicit disclosure

**Source Credibility Assessment:**
- **Tier 1 (Highest):** Major news organizations (Reuters, AP, Bloomberg, WSJ, NYT), official company announcements, government statements
- **Tier 2 (High):** Industry publications, credible tech/business blogs, research reports from reputable firms
- **Tier 3 (Moderate — Verify Carefully):** Social media from verified accounts, company blogs, community discussions
- Minimum 2 credible sources for any claim
- Cross-reference key facts and figures

**Fact Cross-Reference:**
- Verify claims across multiple independent sources
- Use WebFetch to verify any statistics before including them
- Identify potential bias and provide balanced perspective

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

**Required sections:**
- **Executive Summary** — 2-3 sentences highlighting the most important developments across all interest areas
- **High Impact News** — Stories with direct impact on user's projects/role. Each item gets: relevance explanation, detailed summary, impact assessment (projects affected, potential effects, suggested action), sources with credibility tiers and links, confidence level
- **Strategic Developments** — Medium-priority strategic news. Each with: strategic implications list, sourced and confidence-rated
- **Market Intelligence** — Market trends affecting the user. Impact on customers, industry trends, investment patterns
- **Technology Watch** — Relevant tech developments. Impact on tech stack, new tools, emerging tech
- **Competitive Landscape** — Activity from watchlist companies. Recent moves, competitive implications, recommended responses
- **Opportunities & Recommendations** — Action items in Obsidian Tasks format (`📅 YYYY-MM-DD`): immediate actions (today/this week), research needed, people to inform/consult
- **Risks & Threats** — Active threats with mitigation approaches, emerging risks to monitor
- **Verification Report** — Source analysis (counts by tier), fact-checking results (verified/unverified/conflicting claims), freshness verification (all within 7-day window), overall confidence assessment
- **Complete Sources** — Full citations grouped by section, with links

### 4. Handle Special Cases

**When No Recent News Found** for an interest area:
- State clearly: "No significant news found in last 7 days"
- Note last significant development if known
- Suggest expanding search criteria or alternative sources
- NEVER fabricate or use older news without explicit date disclosure

**When Information Cannot Be Verified:**
- Mark with ⚠️ warning
- State what can be confirmed from the single source
- List what's uncertain
- Set confidence to Low
- Recommend monitoring for additional confirmation

**When Sources Conflict:**
- Mark with ⚠️ warning
- Present both perspectives with their source credibility tiers
- List areas of agreement and disagreement
- Recommend resolution approach
- Set confidence to Medium

### 5. Confirm Completion
- Confirm file was created
- Show user: "Daily brief saved to [file path]"
- Optionally show executive summary
- Ask if they want to explore any topic deeper or capture thoughts via braindump skill

## What Good Looks Like

A successful daily brief means: all news is within the 7-day window (100% compliance), every claim has at least 2 credible sources, confidence levels are honestly stated, the brief is relevant to the user's actual interests and projects, and opportunities/risks are actionable — not generic. The user should walk away informed and knowing what to do, not just what happened.
