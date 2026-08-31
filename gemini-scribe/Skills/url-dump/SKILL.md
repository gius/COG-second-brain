---
name: url-dump
description: Quick capture URLs with automatic content extraction, insights, and categorization into knowledge booklets
metadata:
  roles: all
  integrations: web-fetch
  keywords: url dump,save this link,bookmark this,save for later,save url,bookmark,save link,capture url
  display-name: COG Url Dump
---

# COG URL Dump Skill

## Purpose
Transform raw URLs into structured, insightful knowledge entries through intelligent content extraction, categorization, and integration with the user's knowledge base. Quick capture with automatic insight generation.

## When to Invoke
- User shares a URL they want to save
- User says "save this link", "bookmark this", "url dump", or "save for later"
- User pastes a URL and wants to capture it
- User wants to organize web resources into their knowledge base

## Agent Mode Awareness

**Mostly solo.** A single URL save is fast direct work; one sub-agent at ~40K overhead rarely pays off. **Only delegate** (team mode) when batch-processing **3+ URLs** simultaneously: spawn ONE specialist-tier agent that fetches + analyzes all URLs in parallel internally and returns the structured results. Don't spawn one agent per URL.

## Pre-Flight Check

**Before executing, check for user profile:**

1. Look for `00-inbox/MY-PROFILE.md` in the vault
2. If NOT found:
   ```
   Welcome to COG! It looks like this is your first time.

   Before we start, let's quickly set up your profile (takes 2 minutes).

   Would you like to run onboarding first, or should I proceed with default settings?
   ```
3. If found:
   - Read the profile to get user's interests and projects
   - Use interests to help with auto-categorization
   - Check for existing booklet categories in `05-knowledge/booklets/`

**Vault operations and timestamp:** Read `.agents/skills/obsidian/SKILL.md` for vault I/O operations (file creation, search, properties, tags) and follow its timestamp rule and YAML formatting.

## Process Flow

### 1. User Interaction & Input Collection
- Accept URL(s) from the user (single URL or batch)
- Optionally accept user's quick note about why they're saving this
- Accept any format: bare URL, markdown link, or with notes

**Prompt:**
```
What URL(s) would you like to save?
(You can paste one or more URLs, optionally with a note about why you're saving it)
```

### 2. URL Validation & Fetch
- Validate URL format
- Detect duplicate URLs in existing knowledge base
- Fetch the web page content via the fetch ladder (`defuddle` → `WebFetch` → `/playwriter`)

**If the fetch fails** (network error, 403/404, paywall blocking extraction, or every rung of the ladder returns substantially empty content): do NOT proceed to Phase 3 analysis. Instead, save a minimal stub to `00-inbox/url-[title-slug]-YYYY-MM-DD.md` with `status: "fetch-failed"` and the original URL + any user note, and tell the user the fetch failed so they can review manually. Analyzing content that didn't actually load produces plausible-sounding but fabricated insights — exactly the failure mode we're guarding against.

#### Content Extraction
Extract from the fetched page:
- **Page Title:** [extracted-title]
- **Meta Description:** [if available]
- **Author:** [if detected]
- **Published Date:** [if detected]
- **Word Count:** [estimated]
- **Read Time:** [X minutes]
- **Main Content:** [extracted body text]
- **Key Headings:** [list of H1/H2s]

### 3. Category Selection

**Default Categories:**
- **Articles & Blogs:** Long-form content, tutorials, opinion pieces
- **Tools & Resources:** Software, utilities, services, APIs
- **Reference:** Documentation, specs, standards
- **Research:** Papers, studies, academic content
- **Inspiration:** Design, ideas, creative references
- **Videos & Media:** YouTube, podcasts, multimedia
- **News & Updates:** Industry news, announcements
- **Project-Specific:** Related to a specific project (offer project list from MY-PROFILE.md)
- **To Review:** Unsure, save for later categorization

**Custom Categories:**
- Check `05-knowledge/booklets/` for existing custom categories
- Offer to create new category if needed

**Auto-suggestion:** Based on content analysis, suggest the most likely category but let user confirm or change.

### 4. Content Analysis and Processing

#### Phase 1: Content Classification
Determine:
- **Content Category:** [article|tool|reference|research|video|news|etc]
- **Primary Topics:** [topic1, topic2, topic3]
- **Tone:** [informative|opinion|tutorial|news|etc]
- **Quality Assessment:** [high|medium|low]
- **Credibility Indicators:** [author credentials, citations, etc]

#### Phase 2: Insight Extraction
Generate:
- **Executive Summary:** [2-3 sentences]
- **Key Insights:**
  1. [Insight 1 with context]
  2. [Insight 2 with context]
  3. [Insight 3 with context]
- **Notable Quotes:** [if any stand out]
- **Action Items:** [practical takeaways]

#### Phase 3: Relevance Assessment
Analyze:
- **User Interest Match:** [high|medium|low] - [which interests from profile]
- **Project Relevance:** [project-name] - [why relevant]
- **Knowledge Gap:** [yes|no] - [what gap it fills]
- **Timeliness:** [evergreen|current|dated]
- **Uniqueness:** [novel|common|duplicate-adjacent]

#### Phase 4: Cross-Reference
Identify connections to:
- **Related Bookmarks:** [existing similar saves]
- **Related Braindumps:** [if content connects]
- **Related Projects:** [if applicable]
- **Confirms:** [frameworks/patterns from `05-knowledge/_index.md` whose claims this content independently supports — first-hand argument only, not the author citing someone else]
- **Suggested Tags:** [tag1, tag2, tag3]

### 5. Generate Structured Output

Write the file from the bookmark template in `references/output-templates.md`. Read that file now.

Save to appropriate location:
- **Standard:** `05-knowledge/booklets/[category-slug]/[title-slug]-YYYY-MM-DD.md`
- **Project-specific:** `04-projects/[project-slug]/resources/[title-slug]-YYYY-MM-DD.md`
- **Mixed/Unclear:** `00-inbox/url-[title-slug]-YYYY-MM-DD.md`

### 6. Tool/Resource Special Handling

For tools and software, use the tool-entry template in `references/output-templates.md` instead of the bookmark shape.

### 7. Batch Processing

For multiple URLs:

```
Processing [X] URLs...

1. [URL 1] → [category] → Saved to [path]
2. [URL 2] → [category] → Saved to [path]
3. [URL 3] → [category] → Saved to [path]

Summary:
- Articles: 2 saved
- Tools: 1 saved
- Total: 3 URLs processed
```

### 8. Confirm Completion
- Confirm file(s) created
- Show user: "URL saved to [file path]"
- Show quick summary: title, category, key insight preview
- Ask if they want to:
  - Add another URL
  - Deep-dive into the content
  - Connect to specific project or braindump

## Booklet Structure

URLs are organized into "booklets" (category folders):

```
05-knowledge/
└── booklets/
    ├── articles/
    │   ├── _index.md (category overview - auto-created)
    │   └── [article-entries].md
    ├── tools/
    │   ├── _index.md
    │   └── [tool-entries].md
    ├── reference/
    │   ├── _index.md
    │   └── [reference-entries].md
    ├── research/
    │   ├── _index.md
    │   └── [research-entries].md
    ├── inspiration/
    │   ├── _index.md
    │   └── [inspiration-entries].md
    ├── videos/
    │   ├── _index.md
    │   └── [video-entries].md
    └── [custom-category]/
        ├── _index.md
        └── [entries].md
```

### Category Index Template

When creating a new category, also create its `_index.md` from the category-index template in `references/output-templates.md`.

## Edge Cases

- **Paywalled Content:** Note limitation, extract available preview
- **Dynamic Content:** Note if content may change (e.g., live dashboards)
- **Non-English:** Note language, provide translation if possible
- **Low Confidence:** If categorization is unclear, save to inbox and flag for manual review

## After Completion

After saving, suggest relevant follow-ups:
- `/braindump` — if the URL sparked thoughts worth capturing
- `/knowledge-consolidation` — if booklets are piling up and patterns might be emerging
- `/scout` — if the user has more URLs to triage before saving

## Loop Engineering

URL capture is a **fetch-retry loop with a quality gate**, not a single fetch-and-file. See the `loop-engineering` skill for the shared vocabulary.

- **Loop:** fetch → if the body is empty/blocked, retry a different way (https/http, reader mode, archive snapshot) → run the quality gate → file it, or escalate / save to inbox flagged.
- **Verifier (mechanical):** non-empty body (not a paywall stub) · required fields populated (title, ≥1 insight, category) · valid YAML frontmatter · category confidence over threshold.
- **Termination:** gate passes → save · retry cap ~3 fetches → save with low-confidence flag, never invent fields · hard stop on paywall/login wall · below-threshold confidence → ask the user.
- **Patterns:** reflect-retry + evaluator + human-in-the-loop. Process each URL in a batch as its own loop.

## What Good Looks Like

A successful URL capture is fast (under 30 seconds for a single URL), accurately categorized, extracts genuinely useful insights (not just restating the title), and connects to existing vault knowledge where relevant.

## Bundled resources

- [`references/output-templates.md`](references/output-templates.md) - the bookmark entry (step 5), the tool entry (step 6), and the category `_index.md`.
