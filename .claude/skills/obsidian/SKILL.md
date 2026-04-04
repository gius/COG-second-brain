---
name: obsidian
description: >
  Obsidian vault operations reference — CLI commands with direct file I/O fallback, YAML frontmatter rules,
  tags, tasks, and COG vault conventions. Shared reference for all COG skills that interact with the vault.
  When any COG skill creates files, searches the vault, or manages frontmatter, it should follow the
  patterns defined here. For Obsidian-flavored markdown syntax (wiki-links, embeds, callouts, math,
  mermaid), see references/markdown-syntax.md.
metadata:
  roles: all
  keywords: obsidian,vault,frontmatter,yaml,wiki-link,backlink,tags,properties,file-operations,markdown
  display-name: Obsidian Vault Operations
  internal: true
---

# Obsidian Vault Operations

Shared reference for all COG skills that interact with the Obsidian vault.

| Section | What it covers | When to read |
|---|---|---|
| 1-2 | CLI detection, vault operations (create, search, properties, move...) | Any skill doing vault I/O |
| 3 | YAML frontmatter formatting rules | Any skill writing files |
| 4 | Tags — format, hygiene, CLI queries | Any skill creating/searching tags |
| 5 | Obsidian Tasks — emoji format, date calculation | Any skill generating action items |
| 6-7 | COG vault structure, type/status registries | When choosing file paths or frontmatter values |
| `references/markdown-syntax.md` | Wiki-links, embeds, callouts, math, mermaid, footnotes | Skills generating rich Obsidian notes |

**Other skills should reference this file instead of implementing their own vault I/O or formatting logic.**

> CLI command patterns adapted from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) (MIT). COG-specific conventions are original.

---

## 1. CLI Detection (Once Per Session)

Before performing vault operations, determine if the Obsidian CLI is available. Check once and reuse the result for the entire session.

### Step 1: Check integration config

Read `00-inbox/MY-INTEGRATIONS.md` and look for `obsidian_cli` in the active integrations.
- If `MY-INTEGRATIONS.md` doesn't exist → no CLI. Use direct file I/O.
- If `obsidian_cli` is disabled or not listed → no CLI.
- If `obsidian_cli` is active → proceed to availability check.

### Step 2: Check CLI availability

```bash
obsidian vault 2>/dev/null && echo "CLI_AVAILABLE" || echo "CLI_UNAVAILABLE"
```

The `vault` command lists open vaults — only succeeds when Obsidian is running. The `obsidian` binary works on all platforms (Windows, macOS, Linux).

- If `CLI_UNAVAILABLE` → warn user ("Obsidian CLI is configured but Obsidian doesn't appear to be running — falling back to direct file writes").
- If `CLI_AVAILABLE` → use CLI operations throughout.

### Step 3: Vault name

If `MY-INTEGRATIONS.md` has a `vault_name` field under `obsidian_cli`, prepend `vault="VaultName"` as the first parameter to all CLI commands. If not set, omit it (works when only one vault is open).

---

## 2. Vault Operations

Each operation has a **CLI** path and a **Direct** path (always works). Use CLI when available — it keeps Obsidian's index, links, and plugins in sync.

### CLI Syntax Basics

**Parameters** take a value with `=`. Quote values with spaces:
```bash
obsidian create name="My Note" content="Hello world"
```

**Flags** are boolean switches with no value:
```bash
obsidian create name="My Note" silent overwrite
```

For multiline content use `\n` for newline and `\t` for tab.

**File targeting** — many commands accept `file` or `path`:
- `file=<name>` — resolves like a wikilink (name only, no path or extension needed)
- `path=<path>` — exact path from vault root, e.g. `folder/note.md`
- Without either, the active file is used.

**Useful flags:**
- `silent` — prevent the file from opening in Obsidian after creation/modification
- `overwrite` — overwrite existing file (default: fail if exists)
- `total` — on list commands, get a count instead of items
- `--copy` — copy output to clipboard
- `format=json|csv|tsv|md|paths|text|tree|yaml` — structured output

### Create File

**CLI:**
```bash
obsidian create name="<path>" content="<body>" silent
```
Then set frontmatter properties individually via `property:set`. The file is immediately indexed.

Supports templates: `obsidian create name="<path>" template="Template Name" silent`

**Direct:** Write tool with full content (frontmatter + body). `mkdir -p` parent dirs via Bash if needed.

### Append / Prepend

**CLI:**
```bash
obsidian append file="<path>" content="<text>"
obsidian prepend file="<path>" content="<text>"
```

**Direct:** Edit tool to add content at the end/start of the file.

### Read File

**CLI:**
```bash
obsidian read file="<path>"
```

**Direct:** Read tool.

### Set / Remove Property

**CLI:** Atomic and safe — no YAML formatting risk:
```bash
obsidian property:set file="<path>" name="<key>" value="<value>"
obsidian property:remove file="<path>" name="<key>"
```
For array values (themes, tags), pass comma-separated: `value="item1,item2,item3"`

**Direct:** Include properties in the YAML frontmatter block when writing the file. Follow [YAML Frontmatter Rules](#3-yaml-frontmatter-rules).

### Search Vault

**CLI:** Uses Obsidian's pre-built index — faster and more accurate than text search:
```bash
obsidian search query="<term>" format=json
obsidian search query="<term>" limit=10
```

For context around matches: `obsidian search:context query="<term>" limit=5`

**Direct:** Grep tool for file contents, Glob for path patterns.

### Backlinks & Links

**CLI:**
```bash
obsidian backlinks file="<path>" format=json   # Files linking TO this file
obsidian links file="<path>" format=json       # Files this file links TO
```

**Direct:** Grep for `[[filename]]` patterns across the vault.

### Orphans & Unresolved Links

**CLI:**
```bash
obsidian orphans format=json       # Files with no inlinks or outlinks
obsidian unresolved format=json    # Wiki-links pointing to non-existent files
```

**Direct:** Grep for `[[...]]` patterns and cross-reference against existing files (expensive but functional).

### Move / Rename

**CLI:** Updates all backlinks automatically — the single biggest quality win:
```bash
obsidian move file="<path>" to="<destination>"
```

**Direct:** Bash `mv`. Warn the user that backlinks will NOT be updated and may break.

### Delete

**CLI:** Moves to Obsidian trash (recoverable):
```bash
obsidian delete file="<path>"
```

**Direct:** Bash `rm` (not recoverable without git). Prefer CLI when available.

### Daily Notes

**CLI:** Respects the user's configured daily note format and folder:
```bash
obsidian daily              # Open today's daily note
obsidian daily:read         # Read today's daily note
obsidian daily:append content="<text>"  # Append to today's daily note
obsidian daily:path         # Get the file path of today's daily note
```

**Direct:** Detect daily note path manually (typically `01-daily/YYYY-MM-DD.md`) and append via Edit tool.

### List Files

**CLI:**
```bash
obsidian files sort=modified limit=<N> format=json
```

**Direct:** Glob with appropriate patterns.

### Tasks

**CLI:**
```bash
obsidian tasks              # All incomplete tasks
obsidian tasks daily        # Tasks due today
obsidian tasks todo         # Unchecked tasks
```

**Direct:** Grep for `- \[ \]` patterns across the vault.

---

## 3. YAML Frontmatter Rules

All vault files use YAML frontmatter fenced by `---` lines. Obsidian parses this as file properties.

### Formatting Rules

Obsidian uses **js-yaml** (YAML 1.2 core schema). These rules reflect what Obsidian actually parses correctly.

#### Safe without quotes (do not quote)

- **Plain strings** — simple words with no special characters: `type: braindump`, `status: active`, `domain: professional`
- **Booleans** — `true` or `false` (unquoted; Obsidian renders these as checkboxes)
- **Integers** — `priority: 3`, `source_documents: 42`
- **ISO dates** — `date: 2026-04-05` (Obsidian has a native date property type and handles these correctly)
- **Arrays of plain strings** — `themes: [automation, testing, ui-improvements]`

#### MUST quote (will break or silently corrupt if unquoted)

| Value type | Why | Example |
|---|---|---|
| Date-times | js-yaml parses as Date object, loses precision | `created: "2026-04-05 14:30"` |
| URLs | Contain `?`, `&`, `#` — YAML special chars | `url: "https://example.com/path?q=1&v=2"` |
| Wiki-links | `[[` is a YAML flow sequence indicator | `consolidated_in: "[[consolidation-2026-04-03]]"` |
| Strings with `: ` (colon-space) | YAML key-value separator | `title: "My Project: A Deep Dive"` |
| Strings with ` #` (space-hash) | Starts inline YAML comment — rest silently dropped | `note: "See step 3 #important"` |
| Strings starting with `! & * @ > \| % { [` | Reserved YAML characters | `ref: "!important"` |
| Version numbers / floats | `1.0` → parsed as float, `1.10` → becomes `1.1` | `version: "1.10"` |
| Boolean-like words used as strings | `yes`, `no`, `on`, `off` are booleans in YAML 1.1 parsers | `answer: "yes"` |
| Strings containing only digits with leading zeros | `007` may be parsed as octal | `id: "007"` |

#### Tags — Obsidian-specific

Obsidian's official frontmatter format does **NOT** use `#` prefix on tags. The `#` is a body-text convention only. In frontmatter, `#` starts a YAML comment and will silently break parsing if unquoted.

```yaml
# CORRECT — Obsidian official format
tags: [braindump, architecture, api-design]

# ALSO CORRECT (multiline)
tags:
  - braindump
  - architecture

# WORKS BUT NON-STANDARD — Obsidian strips the # anyway
tags: ["braindump", "architecture"]

# BROKEN — # starts a YAML comment, array contents silently lost
tags: [#braindump, #architecture]
```

#### Complete example

```yaml
---
type: braindump
domain: professional
status: captured
themes: [automation, testing, ui-improvements]
tags: [braindump, architecture]
created: "2026-04-05 14:30"
date: 2026-04-05
url: "https://example.com/article"
consolidated_in: "[[consolidation-2026-04-03]]"
analysis_needed: true
source_documents: 42
---
```

### Array Syntax

Obsidian supports both inline and multiline arrays:

```yaml
# Inline (preferred for short lists)
tags: [braindump, architecture]

# Multiline (for longer lists or readability)
tags:
  - braindump
  - architecture
  - api-design
```

### Timestamp Rule

Every file with a `created:` field MUST get its value from the system clock:

```bash
date '+%Y-%m-%d %H:%M'
```

Run this via Bash at the START of the skill, before generating any files. Use the returned value for ALL timestamp fields (`created:`, `date:`, filename date components). NEVER guess or fabricate timestamps.

---

## 4. Tags

Tags categorize vault content and enable filtered views in Obsidian.

### Format

- Tags use the `#` prefix: `#braindump`, `#competitive`, `#project-name`
- In frontmatter arrays: `tags: ["braindump", "architecture"]`
- Inline in text: `#tag` anywhere in the document body
- Use kebab-case for multi-word tags: `#weekly-checkin`, `#auto-research`
- Nested tags use `/`: `#project/saas-product`
- Valid characters: letters, numbers (not first char), underscores, hyphens, forward slashes

### Tag Hygiene

- **Prefer existing tags** — check what's in the vault before inventing new ones
- **Use near-matches:** vault has `#architecture` → don't create `#arch`
- **Skill-specific tags:** each skill has a primary tag matching its type (`#braindump`, `#daily-brief`, `#prd`). Always include it.
- **Domain tags:** add domain-relevant tags beyond the skill tag (`#api`, `#competitive`, `#leadership`)

### Querying Tags

**CLI:**
```bash
obsidian tags format=json              # All tags with counts
obsidian tags sort=count counts        # Sorted by usage
obsidian tag tag="#specific-tag"        # Files with this tag
obsidian tags:rename old="oldtag" new="newtag"  # Bulk rename
```

**Direct:** Grep for tag patterns in frontmatter across the vault.

---

## 5. Obsidian Tasks

COG uses the [Obsidian Tasks emoji format](https://publish.obsidian.md/tasks/Reference/Task+Formats/Tasks+Emoji+Format) for all action items:

```markdown
- [ ] Action item description 📅 YYYY-MM-DD
- [x] Completed item 📅 YYYY-MM-DD ✅ YYYY-MM-DD
```

### Date Calculation

When generating tasks, calculate actual dates from the current date:

| Timeframe | How to calculate |
|---|---|
| Immediate (24-48 hours) | Tomorrow's date |
| Short-term (1-2 weeks) | +1 week from today |
| Today / This week | Today or end of current week (Friday) |
| Next steps | Next Monday or Friday |

Always use real calendar dates, never relative text like "next week" or "soon".

---

## 6. COG Vault Structure

The standard COG vault layout (created by `/onboarding`):

```
00-inbox/              # Uncategorized, config files, mixed-domain content
  MY-PROFILE.md
  MY-INTERESTS.md
  MY-INTEGRATIONS.md
  archive/             # Archived/superseded content

01-daily/              # Time-bound outputs
  briefs/              # Daily briefs
  checkins/            # Weekly check-ins

02-personal/           # Personal domain
  braindumps/
  development/
  wellness/

03-professional/       # Professional domain
  braindumps/
  leadership/
  strategy/
  COMPETITIVE-WATCHLIST.md

04-projects/           # Project-specific content
  [project-slug]/
    PROJECT-OVERVIEW.md
    braindumps/
    competitive/
    content/
    planning/
    resources/
    stories/
    PRDs/
    release-notes/
    audits/
    meetings/

05-knowledge/          # Knowledge base
  consolidated/        # Frameworks and consolidations
  patterns/            # Pattern analyses
  timeline/            # Evolution timelines
  booklets/            # URL booklets by category
  research/            # Auto-research outputs
  [domain]/            # KB entries by domain (product/, technical/, process/)
  _logs/               # KB update logs

06-templates/          # Obsidian templates
```

### File Naming

Skill outputs follow the pattern: `<type>-YYYY-MM-DD-HHMM-<slug>.md` or `<type>-YYYY-MM-DD.md` (when only one per day is expected). The slug is a kebab-case summary (e.g., `braindump-2026-04-03-1705-api-graphql-migration.md`).

---

## 7. COG Registries

### Document Type Registry

| `type` value | Created by skill |
|---|---|
| `"braindump"` | braindump |
| `"competitive-intelligence"` | braindump |
| `"daily-brief"` | daily-brief, team-brief |
| `"weekly-checkin"` | weekly-checkin |
| `"meeting-transcript"` | meeting-transcript |
| `"url-bookmark"` | url-dump |
| `"url-tool"` | url-dump |
| `"booklet-index"` | url-dump |
| `"prd"` | generate-prd |
| `"release-notes"` | generate-release-notes |
| `"open-issues-audit"` | export-open-issues |
| `"knowledge"` | update-knowledge-base |
| `"kb-update-log"` | update-knowledge-base |
| `"consolidated-knowledge"` | knowledge-consolidation |
| `"pattern-analysis"` | knowledge-consolidation |
| `"timeline-entry"` | knowledge-consolidation |
| `"knowledge-consolidation"` | knowledge-consolidation |
| `"vault-health-audit"` | knowledge-consolidation |
| `"profile"` | onboarding |
| `"interests"` | onboarding |
| `"integrations"` | onboarding |
| `"competitive-watchlist"` | onboarding |
| `"project-overview"` | onboarding |
| `"auto-research"` | auto-research |

### Status Values

| `status` value | Meaning | Used by |
|---|---|---|
| `"captured"` | Initial state, unprocessed | braindump |
| `"consolidated"` | Processed into frameworks | braindump (after consolidation) |
| `"unread"` | Not yet reviewed | url-dump (bookmarks) |
| `"to-evaluate"` | Pending evaluation | url-dump (tools) |
| `"draft"` | Work in progress | generate-prd |
| `"deprecated"` | Superseded or outdated | update-knowledge-base, knowledge-consolidation |
| `"stable"` / `"working"` / `"emerging"` | Framework maturity | knowledge-consolidation |
| `"published"` | Published externally | publish-to-confluence |

### Common Frontmatter Fields

| Field | Type | Description |
|---|---|---|
| `type` | string | Document type (see registry above) |
| `domain` | string | `"personal"`, `"professional"`, `"project-specific"`, `"mixed"` |
| `project` | string | Project name (only if project-specific) |
| `date` | string | `"YYYY-MM-DD"` |
| `created` | string | `"YYYY-MM-DD HH:MM"` (from system clock) |
| `themes` | array | `["theme1", "theme2"]` |
| `tags` | array | `["tag1", "tag2"]` |
| `status` | string | Document lifecycle state |
| `confidence` | string | `"high"`, `"medium"`, `"low"` |
