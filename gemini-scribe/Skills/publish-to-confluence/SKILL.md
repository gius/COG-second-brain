---
name: publish-to-confluence
description: Publish any markdown file from the vault to Confluence with format conversion and approval gate
metadata:
  roles: product-manager,engineering-lead,founder
  integrations: confluence
  keywords: publish to Confluence,push to wiki,send to Confluence,confluence publish
  display-name: COG Publish To Confluence
---

# COG Publish to Confluence Skill

## When to Invoke
- User wants to publish a document to Confluence
- User says "publish to Confluence", "push to wiki", "send to Confluence", "confluence publish"
- User has a markdown file they want to share with the team on Confluence
- After generating a PRD, release notes, or other document that should go to the wiki

## Agent Mode Awareness

**Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:**
- If `agent_mode: team` — no significant benefit for this skill (single sequential operation)
- If `agent_mode: solo` — standard execution

## Command: `/publish-to-confluence`

## Pre-Flight Check

1. **Read `00-inbox/MY-INTEGRATIONS.md`** — Confluence MUST be listed under Active Integrations
   - If Confluence is **not active**: Inform the user and stop.
     ```
     Confluence is not in your active integrations.

     Would you like to:
     a) Set up Confluence integration (I'll add it to MY-INTEGRATIONS.md)
     b) Export the document in a Confluence-compatible format for manual upload
     ```
   - If Confluence is **disabled**: Skip silently per COG conventions. Suggest alternative publishing (HackMD, Notion) if active.

2. **Vault operations:** Read `.agents/skills/obsidian/SKILL.md` for timestamp rule, property management, and YAML formatting


## Execution Strategy

### Phase 1: Identify the Source Document

Determine what to publish:

**Option A: User specifies a file path**
```
Read the specified file from the vault.
```

**Option B: User describes the document**
```
Search for matching files:
1. Glob for likely matches in 04-projects/, 05-knowledge/, 01-daily/
2. Present candidates and let user choose
```

**Option C: Just-generated document**
If this skill is invoked right after generating a PRD, release notes, or other document, use that document.

### Phase 2: Configure Publishing Target

Ask the user (if not already provided):

```
Where should this be published in Confluence?

Required:
- Space key: [CUSTOMIZE: YOUR-SPACE-KEY] (or let me search for spaces)
- Parent page: [Page title or ID under which to nest this page]

Optional:
- Page title: [defaults to the document's H1 heading]
- Labels: [Confluence labels to add]
- Publish mode: "create new" or "update existing"
```

**If the user doesn't know the space or parent page:** list spaces and pages with the Atlassian integration's read tools (Claude: `searchConfluence` / `getConfluenceContent`, with the `cloudId` from `getAccessibleAtlassianResources`) and let the user choose.

### Phase 3: Prepare the Page Body

The Atlassian integration accepts markdown or HTML page bodies, so no hand conversion to storage XHTML is needed. Prepare the body:

- Strip YAML frontmatter.
- Turn vault wiki-links (`[[note]]`, `[[note|alias]]`) into plain text (the alias if present); they do not resolve in Confluence.
- Keep tables, nested lists, code blocks, task lists and emoji as they are.
- Before writing, read the integration's authoring guide for the target tool (Claude: `getContentFormatGuide`) and the space's instructions (`getConfluenceSpace`), and apply them.

### Phase 4: Preview and Approval Gate

Publish only after the user approves this preview - a published page is visible to the whole space at once.

Present a summary to the user:

```
Ready to publish to Confluence:

Document: [filename]
Title: [page title]
Space: [space key]
Parent Page: [parent page title]
Mode: [create new / update existing]
Labels: [labels]

Content preview (first 500 chars):
[preview text]

Estimated page size: [approximate word count]

Proceed with publishing? (yes/no)
```

**Wait for explicit "yes" before proceeding.**

### Phase 5: Publish

Needs an Atlassian integration with write access. If `00-inbox/MY-INTEGRATIONS.md` lists only read scopes, stop after Phase 4 and offer the prepared body as a file for manual paste.

#### Create new page
Create the page with the integration's create tool (Claude: `createConfluenceContent`, `contentType: "page"`, `parent: {spaceId, parentContentId}`, `body: {format: "markdown", value: ...}`). Add labels afterwards if the user asked for them.

#### Update existing page
1. Read the current page in full (Claude: `getConfluenceContent`, `detail: "full"`, `content_format: "html"`) - this returns the `snapshotToken` the update needs.
2. If the page body contains macros (table of contents, page properties, excerpts, Jira embeds), do not replace the whole body - a markdown replacement drops them. Use granular edits (`edits`) on the changed sections, or send back the fetched HTML with only the prose sections replaced.
3. Otherwise replace the body (Claude: `updateConfluenceContent` with `snapshotToken` and `body`). A `dryRun: true` call first shows the result without saving.

### Verify

Read the page back by ID (Claude: `getConfluenceContent`, `detail: "full"`). Confirm the title, the parent, a version number higher than before (update) and a body that contains the document's headings. On any mismatch, tell the user what differs and do not report success.

### Phase 6: Confirm and Update Vault

After the Verify step passes:

1. **Confirm to the user:**
   ```
   Published and verified.

   Page: [Title]
   URL: [Confluence page URL]
   Space: [Space Key]
   Version: [version number]
   ```

2. **Update the source vault file** (add published metadata to frontmatter):
   ```yaml
   confluence_url: "[page URL]"
   confluence_page_id: "[page ID]"
   confluence_space: "[space key]"
   published_at: "[timestamp]"
   confluence_version: [version number]
   ```

3. **Log the publication** for future reference.


## Re-Publishing (Update Flow)

If the vault file already has `confluence_page_id` in its frontmatter:

```
This document was previously published to Confluence:
  URL: [confluence_url]
  Last published: [published_at]

Would you like to:
a) Update the existing Confluence page (increment version)
b) Create a new page (separate copy)
c) Cancel
```


## Fallback Behavior

| Scenario | Behavior |
|----------|----------|
| Confluence not active | Stop and inform user; suggest alternative platforms |
| Integration call fails | Save the prepared body to a file so the user can paste it manually |
| Authentication failure or read-only access | Tell the user the integration needs re-authentication or write access |
| Page already exists (same title) | Ask user: update existing, create with different title, or cancel |
| Very large document | Warn user about page size; suggest splitting into child pages |
| Complex markdown (unsupported elements) | Convert best-effort, warn about any elements that couldn't be converted |

## Error Handling

- **API 403 (Forbidden)**: User may lack write permissions to the target space
- **API 404 (Not Found)**: Space key or parent page ID may be incorrect
- **Conflict / stale snapshot**: Page was modified by someone else; re-read it for a fresh `snapshotToken` and retry
- **Conversion failures**: Fall back to plain text for elements that can't be converted
- **Network errors**: Save converted content locally so no work is lost
