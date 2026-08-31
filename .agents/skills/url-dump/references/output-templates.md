# url-dump: output templates

The three file shapes this skill writes. Read this file at step 5, and again at step 6 if the URL is a tool.

## Bookmark entry

Step 5. The default shape for an article, post, or paper.

```markdown
type: "url-bookmark"
category: "[category-name]"
domain: "[source-domain.com]"
date_saved: "YYYY-MM-DD"
date_accessed: "YYYY-MM-DD HH:MM"
url: "[original-url]"
title: "[page-title]"
author: "[author-if-available]"
published: "[publish-date-if-available]"
tags: ["bookmark", "category-tag", "topic-tags"]
relevance: "[high|medium|low]"
status: "unread"
related_projects: ["project1", "project2"]
needs_review: false  # set true only if categorization is ambiguous enough that a human should double-check

# [Title]

## Quick Summary
[2-3 sentence summary of the content]

## Key Insights
- **Insight 1:** [description with context]
- **Insight 2:** [description with context]
- **Insight 3:** [description with context]

## Why This Matters
[Connection to user's interests/projects. What makes this worth saving?]

## User Note
[Original user note if provided, otherwise omit section]

## Content Highlights
[Key excerpts or quotes from the content - 200-400 words max]

## Confirms
[Only when the content independently supports an existing framework/pattern from `05-knowledge/_index.md`; omit the section otherwise]
- **[claim in one phrase].** "[supporting quote]" → [[framework-or-pattern]]

## Practical Takeaways
- [ ] [Action item 1 if applicable] 📅 [YYYY-MM-DD = date +1 week from today]
- [ ] [Action item 2 if applicable] 📅 [YYYY-MM-DD = date +1 week from today]

## Related Knowledge
- **Similar Bookmarks:** [[bookmark1]], [[bookmark2]]
- **Connected Projects:** [[project1]]
- **Related Notes:** [[note1]], [[note2]]

## Source Details
| Field | Value |
|-------|-------|
| Domain | [domain] |
| Author | [author or "Unknown"] |
| Published | [date or "Unknown"] |
| Word Count | [~X words] |
| Read Time | [~X minutes] |

## Processing Notes
- **Extracted:** [timestamp]
- **Review Needed:** [yes|no] - [reason if yes - e.g. "categorization ambiguous between Articles and Research", "paywalled preview only"]


*Processed by COG URL Curator*
```

## Tool or resource entry

Step 6. Use instead of the bookmark shape when the URL is a tool or a piece of software.

```markdown
type: "url-tool"
category: "tools"
domain: "[domain]"
url: "[url]"
title: "[tool-name]"
date_saved: "YYYY-MM-DD"
pricing: "[free|freemium|paid|enterprise]"
tags: ["tool", "category-tags"]
status: "to-evaluate"

# [Tool Name]

## What It Does
[1-2 sentence description]

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Use Cases
- Use case 1
- Use case 2

## Pricing
[Pricing details if available]

## Why It's Relevant
[Connection to user's work/interests]

## Evaluation Status
- [ ] Sign up / try demo 📅 [YYYY-MM-DD = date +3 days from today]
- [ ] Test key features 📅 [YYYY-MM-DD = date +1 week from today]
- [ ] Compare with alternatives 📅 [YYYY-MM-DD = date +1 week from today]
- [ ] Decision: [use|pass|revisit] 📅 [YYYY-MM-DD = date +2 weeks from today]

## Notes
[Space for user's evaluation notes]


*Processed by COG URL Curator*
```

## Category index

Created once per new booklet category, at `05-knowledge/booklets/<category-slug>/_index.md`.

```markdown
type: "booklet-index"
category: "[category-name]"
created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
entry_count: 0

# [Category Name] Booklet

## Description
[What this category contains]

## Recent Additions
[Auto-updated list - most recent 10 entries]

## Top Entries
[Manually curated or most-accessed entries]

## Tags in This Category
[List of common tags used]

## Related Categories
- [[other-category-1]]
- [[other-category-2]]
```
