---
name: scout
description: "Investigate one URL, library, or article in depth: read it, gather verified external signal (reviews, comments, reactions), check vault coverage, recommend save / read-in-full / skip"
metadata:
  roles: all
  integrations: web-fetch,web-search
  keywords: scout,scout this,investigate,evaluate,should I save this,is this relevant,worth reading,deep dive on this link
  display-name: COG Scout
---

# COG Scout Skill

## Purpose
Deep investigation of a single artifact (a URL, library/tool/repo, or article) before you commit time to it. Scout reads the thing, gathers verified external signal (reviews, comments, reactions, comparisons), checks whether the vault already covers the substance, and gives one clear recommendation. It does the reading so you do not have to.

## When to Invoke
- "scout this", "investigate this", "is this worth reading?", "should I save this?"
- User shares a link/library and wants a read + verdict, not just a metadata glance
- A `/daily-brief` or `/auto-research` surfaced a tool or article worth a closer look

## Pre-Flight
- Read `00-inbox/MY-PROFILE.md` (active projects, role) and `00-inbox/MY-INTERESTS.md` for relevance scoring. If missing, evaluate on general quality and ask if they want `/onboarding`.
- Confirm `web-fetch` is active in `00-inbox/MY-INTEGRATIONS.md`. If not, fetch is unavailable - say so and work from what the user can paste.

## Process

### 1. Classify the input
- **Library / tool / repo** - assess by docs + reputation
- **Article / post / paper** - assess by reading the content
- **Open-ended question** (not a single artifact) - hand off to `/auto-research`, do not scout

### 2. Read the primary source
Fetch and read it fully, not just title/author/date.
- Default: `WebFetch`
- JS-heavy / login-walled / lazy-loaded (Reddit, X, Disqus, Instagram): use `/playwriter`
- X/Twitter posts: read via `api.vxtwitter.com`
- Auth-gated / paywalled (e.g. X Articles `x.com/i/article/...`, which vxtwitter and WebFetch cannot return): try an `archive.today` snapshot first - `https://archive.ph/newest/<url>` - then fall back to `/playwriter` on the live session

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

### 5. Recommend (pick one, with evidence)
- **Adopt / Try** - strong fit, healthy signal, worth using
- **Save** - worth keeping; hand off to `/url-dump`
- **Read in full** - high value, deserves your own read; flag the 2-3 sections worth your time
- **Skip - already covered** - vault already holds the substance (point to the note)
- **Skip - low value** - weak signal, wrong stack, or thin content (say why)

Present: a tight overview of what it says, the verified external signal, the coverage finding, then the one recommendation.

## Agent Mode
- **team:** delegate each external-source lookup to a worker (Haiku). Brief each with the verification rules in step 3 - primary source, fetch + proof, drop rule. Synthesize in the main conversation.
- **solo:** do all fetching and reading directly.

## Handoff
- **Save** -> `/url-dump` with a pre-filled category + any step-4 framework/pattern overlaps as `## Confirms` targets
- **Open-ended question** -> `/auto-research`
