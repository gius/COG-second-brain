---
name: scout
description: "Investigate one URL, library, or article in depth: read it, gather verified external signal, check vault coverage, refresh vault notes it proves stale, flag what it offers the user's other projects, and give one verdict - adopt / save / read-in-full / skip. Use whenever the user shares a single link, library, repo or article and wants a judgement rather than a metadata glance - 'scout this', 'investigate this', 'is this worth reading', 'should I save this', 'does this change anything for my projects' - or when a /daily-brief or /auto-research surfaced something worth a closer look. Use it even when the user does not say 'scout'."
metadata:
  roles: all
  integrations: web-fetch,web-search
  keywords: scout,scout this,investigate,evaluate,should I save this,is this relevant,worth reading,deep dive on this link,does this change anything,what does this mean for my projects
  display-name: COG Scout
---

# COG Scout Skill

## Purpose
Deep investigation of a single artifact (a URL, library/tool/repo, or article) before you commit time to it. Scout reads the thing, gathers verified external signal (reviews, comments, reactions, comparisons), checks whether the vault already covers the substance, refreshes vault notes the source proves outdated, flags what it offers the user's other projects, and gives one clear recommendation. It does the reading so you do not have to.

## Pre-Flight
- Read `00-inbox/MY-PROFILE.md` (active projects, role) and `00-inbox/MY-INTERESTS.md`. Keep the active-project list - step 6 scores against it. Missing: evaluate on general quality and ask if they want `/onboarding`.
- Fetching needs no integration check. If every rung of the step-2 ladder fails, say so and ask the user to paste the content.

## Process

Steps 5 and 6 always run; they report only on a hit. The user never has to ask "does this make anything stale?" or "is this useful elsewhere?"

### 1. Classify the input
- **Library / tool / repo** - assess by docs + reputation
- **Article / post / paper** - assess by reading the content
- **Open-ended question** (not a single artifact) - hand off to `/auto-research`, do not scout

### 2. Read the primary source
Fetch and read it fully, not just title/author/date.

Ladder, in order - fall through on error, empty body, or elided content:
1. `defuddle parse <url> --md` - static pages
2. `WebFetch` - when defuddle is absent or returns nothing
3. `/playwriter` - JS-heavy, login-walled, lazy-loaded

Exceptions:
- JS-rendered domains (Reddit, X, Disqus, Instagram): start at rung 3; rungs 1-2 return an empty shell
- X/Twitter posts: `api.fxtwitter.com`, falling back to `api.vxtwitter.com`
- Auth-gated / paywalled (e.g. X Articles `x.com/i/article/...`, which neither rung 1 nor 2 can return): try `https://archive.ph/newest/<url>`, then `/playwriter` on the live session
- Medium (`medium.com`, `*.medium.com`, Medium-hosted custom domains) 403s on all three rungs: prepend `https://r.jina.ai/` to the full URL - markdown plus title and date - or `https://freedium-mirror.cfd/` as fallback
- `.md` URLs and raw API endpoints: fetch directly, skip the ladder

### 3. Gather external signal (input-aware)
- **Library:** open GitHub issues, HN/Reddit threads, "X vs Y" comparisons, release cadence, maintenance/adoption health
- **Article:** comment section, discussion threads, notable counter-takes

**Verification (non-negotiable - this is what makes Scout save time instead of mislead):**
- Every quoted review/comment/reaction must trace to a fetched URL. Include the fetched title + date as proof.
- Drop anything you cannot fetch. Do not paraphrase a "representative" reaction from memory.
- "No real reactions found" is a valid, useful result. Fabricated signal is not.

### 4. Vault coverage (substance, not just URL)
- **Exact:** grep the vault for the URL / domain / library name (catches a literal re-save).
- **Substance:** pull 3-5 key claims/entities from what you just read, grep vault titles, headers, body, and tags for them, read the hits, and judge real overlap vs a passing mention. Quote the overlapping note and let the user decide - a keyword hit is not proof they have already absorbed this.

### 5. Refresh what the source proves stale
Step 4 already read the overlapping notes. Compare them against what the source says. No extra scan, no user prompt to start it.

**Staleness = the vault states something the source falsifies:** superseded version or API, dead/renamed/archived project, moved URL, changed pricing or licence, a claim the source disproves.

**Where it may be written:**

| Target | Action |
|---|---|
| Living doc (undated - `PROJECT-OVERVIEW.md`, `architecture.md`, booklet entry, `05-knowledge/patterns/`) | Edit in place |
| Dated doc (`reports/`, `braindumps/`, `research/<x>-YYYY-MM-DD.md`) | Never rewrite - point-in-time record. Append one dated correction line, or leave it and cite the newer source in the report |
| `05-knowledge/consolidated/` framework | Never edit. Append one line to `05-knowledge/_index.md` -> **Open Contradictions**; only `/knowledge-consolidation` resolves it |

**Ask first vs edit now:**
- **Edit now, report after** - the correction is a fact: version, name, URL, status, price, a falsified claim.
- **Ask first** - the correction changes a decision, plan, or recommendation ("we picked X because it does Y" and it no longer does).

Every in-place edit carries a dated changelog line naming the source URL. State the source date so a reader can tell which is newer.

Report as `## Refreshed` only when a file changed - file, what changed, one-line evidence. Never manufacture an edit to fill the section. Nothing stale: emit no section and no justification - one clause in the verdict.

### 6. Cross-project relevance
Score the source against the active projects from `00-inbox/MY-PROFILE.md`. Where a hit looks plausible, read that project's `PROJECT-OVERVIEW.md` and backlog to check the need is real and not already solved.

Look for: a feature or approach that solves a known open problem, a library that replaces something hand-rolled, a benchmark or number that settles an open decision, a failure mode the project would hit.

Report as `## Relevant to your projects` only on a hit - project, the specific thing, suggested action (one line each). Skip the slot if it is only "interesting"; the tie-in must name what it changes.

**No forced tie-ins.** Nothing carries over: emit no section and no per-project list - one clause in the verdict. Never one bullet per active project.

### 7. Recommend (pick one, with evidence)
- **Adopt / Try** - strong fit, healthy signal, worth using
- **Save** - worth keeping; hand off to `/url-dump`
- **Read in full** - high value, deserves your own read; flag the 2-3 sections worth your time
- **Skip - already covered** - vault already holds the substance (point to the note)
- **Skip - low value** - weak signal, wrong stack, or thin content (say why)

Use this structure. Omit any section with no content - never emit a heading to announce that nothing was found:

```markdown
# <name> - <verdict>
<tight overview of what it says>
## <signal heading>      <- verified external signal, quoted with permalinks
## <coverage heading>    <- vault overlap, quoting the overlapping note
## Refreshed             <- only when a file changed
## Relevant to your projects  <- only on a hit
## Verdict
<the one recommendation, with evidence, closing with the null-result clause>
```

Null results from steps 5 and 6 collapse into one clause in the verdict - no heading, no evidence, no per-project list.

**Example verdict, both checks null:**
```markdown
**Skip - low value.** Abandoned five months ago, no adoption, no discussion, and every one of
its seven skills already exists in COG in a deeper form. Nothing stale, nothing carries over.
```

## Agent Mode
- **team:** delegate each external-source lookup to a **specialist-tier** sub-agent. Brief each with the verification rules in step 3 - primary source, fetch + proof, drop rule. Synthesize in the main conversation.
- **Not worker tier.** `WebFetch` caps quotes at ~125 chars and elides silently. Noticing the elision and climbing to rung 3 is a judgment call worker tier misses, and an elided quote returned as verbatim is worse than a dropped one.
- **Sub-agents fetch, they never write.** Steps 5 and 6 - vault edits, the Open Contradictions append, project scoring - run in the main conversation.
- **solo:** do all fetching and reading directly.

## Handoff
- **Save** -> `/url-dump` with a pre-filled category + any step-4 framework/pattern overlaps as `## Confirms` targets
- **Step 5 raised a plan-level contradiction** -> `/knowledge-consolidation` to resolve the Open Contradictions entry
- **Step 6 hit is worth acting on** -> a task in the project's doc, Obsidian emoji format `- [ ] <action> 📅 YYYY-MM-DD`
- **Open-ended question** -> `/auto-research`
