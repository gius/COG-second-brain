---
type: guide
created: 2026-02-23
updated: 2026-08-14
status: active
audience: family
---

# COG Family Setup Guide

Set up your AI-powered second brain. This is the only setup guide - if you have an
older one saved anywhere, throw it away.

**What is COG?** A system that helps you capture thoughts, get personalized news,
reflect on your week, and build knowledge over time. Everything is stored as text
files on your computer - private, yours.

**What is Gemini Scribe?** An Obsidian plugin that puts an AI assistant in a side
panel next to your notes. It can read your whole vault, write and edit notes, search
the web, and run on a schedule.

**What changed (August 2026):**

- **Setup is one PowerShell line.** `cog-install.ps1` installs Git and Obsidian,
  clones the vault, and drops in all four plugins. See [One-Time Setup](#2-one-time-setup).
- **Gemini Scribe reached three providers** - Gemini, Ollama, and OpenAI - and can
  route each feature to a different one. See [Models & Alternatives](#9-models--alternatives).
- New skill: **daily journal**, a short work log the assistant writes for you.

**What changed (July 2026):**

- **Obsidian + Gemini Scribe replaces OpenCode.** One app instead of two, no black
  terminal window, no browser tab. See [Migrating from OpenCode](#8-migrating-from-opencode)
  if you already had the old setup.
- The vault clone is now a plain **HTTPS** link - no GitHub account, no SSH key.
- Gemini Scribe works on **phones and tablets** with the same setup as the desktop.
- COG skills ship pre-installed in `gemini-scribe/Skills/`.

---

## Table of Contents

1. [Quick Overview](#1-quick-overview)
2. [One-Time Setup (Gusta does this)](#2-one-time-setup)
3. [Your First Time Using COG](#3-your-first-time-using-cog)
4. [Daily Cheat Sheet](#4-daily-cheat-sheet)
5. [Working With Context](#5-working-with-context)
6. [Updating COG](#6-updating-cog)
7. [Troubleshooting](#7-troubleshooting)
8. [Migrating from OpenCode](#8-migrating-from-opencode)
9. [Models & Alternatives](#9-models--alternatives)

---

## 1. Quick Overview

COG uses **Google AI Studio** with **Gemini 3 Flash**. Gusta creates an API key linked
to billing. Each family member gets their own key.

**Costs:**

| Usage Level | Estimated Cost | Notes |
|---|---|---|
| Light (a few sessions/week) | ~$0.10-0.30/mo | Most family members |
| Daily (brief + braindump every day) | ~$0.30-1/mo | Active users |
| Heavy (multiple long sessions/day) | ~$1-3/mo | Power users |

A typical COG session costs well under a cent. **Gusta manages billing** - just use it.

> Current per-token prices are at
> [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing).
> Check there before quoting a number - model prices change.

**Sync architecture:**

- Vault lives in your **OneDrive folder** on your desktop
- OneDrive auto-syncs across all your desktops on the same Microsoft account
- On Android/iOS, the **Remotely Save** Obsidian plugin pulls the vault on demand

---

## 2. One-Time Setup

> Gusta does this for each family member's desktop. You don't do this yourself.

### Step 1: Run the installer

Open PowerShell and paste this one line:

```powershell
irm https://raw.githubusercontent.com/gius/COG-second-brain/feature/custom-changes/cog-install.ps1 | iex
```

It installs Git and Obsidian, clones the vault, and downloads the four Obsidian
plugins. Every step skips itself if it is already done, so it is safe to re-run. The
script is `cog-install.ps1` in the vault folder if you want to read it first.

**It asks before it installs anything.** The first thing it prints is the folder it
intends to use:

```
Vault folder:  C:\Users\jana\OneDrive\cog-second-brain

Press Enter to use it, or type a different full path (or "q" to quit)
```

Press Enter to accept. Type a full path to put the vault somewhere else - it re-checks
each time, and refuses paths that can't work (a folder that already has files in it, or
one whose parent doesn't exist). It warns, but still allows, a folder outside personal
OneDrive: that costs you phone sync. Nothing is installed until you answer.

**What it sets up:**

| Thing | Where it lands |
|---|---|
| Git, Obsidian | `winget install Git.Git`, `winget install Obsidian.Obsidian` |
| Vault content | `%OneDrive%\cog-second-brain` by default, confirmed on screen first - OneDrive auto-syncs it to your phone and other desktops |
| Git database | `%USERPROFILE%\.cog-git\cog.git` - **outside** OneDrive, so OneDrive doesn't sync git's thousands of tiny internal files (slow, and it breaks the repo) |
| Plugins | Gemini Scribe, Tasks, Calendar, Remotely Save → `.obsidian\plugins\` |

The vault is cloned from Gusta's family COG fork on the `feature/custom-changes`
branch, public over HTTPS - no GitHub account, no SSH key, no login. A tiny `.git`
pointer file stays inside the OneDrive folder. **Don't delete it** - it's how
`cog-update.bat` finds the git data.

<details>
<summary>Manual install, if you would rather not run a script</summary>

Install [Git](https://git-scm.com) and [Obsidian](https://obsidian.md) (both free),
then:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cog-git" | Out-Null
git clone -b feature/custom-changes https://github.com/gius/COG-second-brain.git `
  --separate-git-dir="$env:USERPROFILE\.cog-git\cog.git" `
  "$env:USERPROFILE\OneDrive\cog-second-brain"
```

Then install four plugins from Settings → **Community plugins** → **Browse**:
**Gemini Scribe**, **Tasks**, **Calendar**, **Remotely Save**.

</details>

> **Git is not optional.** `cog-update.bat` runs `git pull`, so a vault downloaded as
> a ZIP instead of cloned can never be updated.

### Step 2: Open the vault

1. Open Obsidian → **Open folder as vault**
2. Select `%USERPROFILE%\OneDrive\cog-second-brain`
3. Settings → **Community plugins** → click **Turn on community plugins** if Obsidian
   asks for it. The four plugins are already on disk; switch on any that show as off.

| Plugin | What it does |
|---|---|
| **Gemini Scribe** | The AI assistant in the side panel |
| **Tasks** | Track to-dos with due dates across all your notes |
| **Calendar** | Visual calendar sidebar |
| **Remotely Save** | Mobile sync via OneDrive (see Step 5) |

### Step 3: Add the API key

Gusta creates a key at [aistudio.google.com](https://aistudio.google.com/apikey) and
links it to billing.

1. Settings → **Gemini Scribe** → **General**
2. **Provider**: `Google Gemini (cloud)`
3. Paste the API key
4. **Chat model**: `gemini-3-flash-preview`

That's the whole connection. Nothing to install in a terminal, no login flow.

### Step 4: Point the plugin at COG's skills

COG ships its skills in the `gemini-scribe` folder inside the vault, which is where
the plugin expects them.

1. Settings → **Gemini Scribe** → **General** → **Plugin state folder**
2. Click the field and pick **`gemini-scribe`** from the dropdown

To confirm it worked: open the chat panel and type `/` on an empty input. You should
see `braindump`, `daily-brief`, `weekly-checkin` and the rest in the list.

> The vault ships `gemini-scribe/AGENTS.md`, which tells the assistant how COG is
> organized. It loads automatically. **Don't click "Initialize vault context"** - that
> overwrites the tuned version with a generic one.

### Step 5: Mobile setup (optional)

#### Vault sync

1. On Android/iOS, install **Obsidian** from the app store (free)
2. Create a new vault with the **same name** as your desktop vault: `cog-second-brain`
3. Install **Community plugins → Browse → "Remotely Save"**
4. In Remotely Save settings:
   - Remote Service: **OneDrive**
   - Click **Auth**, log in with the same Microsoft account as desktop
   - Tap the sync arrow in the sidebar for the first sync

**Caveats:**

- Works with **OneDrive Personal** only - NOT OneDrive for Business
- **No background sync** - you must open Obsidian and tap sync
- First sync can take a while on a slow connection

#### Mobile AI

Install **Gemini Scribe** on mobile too and paste the same API key. Unlike the old
setup, the phone gets the *same* assistant as the desktop - it can write notes and run
skills, not just answer questions.

> On mobile, consider turning on confirmation for `write_file` and `delete_file`
> (Settings → Gemini Scribe → Tool permissions) so a mistyped request can't quietly
> change a note.

---

## 3. Your First Time Using COG

### Opening the assistant

Click the **sparkles icon (✨)** in the left ribbon, or use the command palette
(`Ctrl+P`) → "Gemini Scribe: Open Gemini chat".

### Run Onboarding

Type:

```
Run onboarding
```

Answer naturally:

> "I'm Jana, a student interested in biology, art, and sustainability. I'm working on
> a school project about local ecosystems."

The AI creates `00-inbox/MY-PROFILE.md`, `00-inbox/MY-INTERESTS.md`, and project
folders if you mentioned any. Takes about 2 minutes.

### Try Your First Braindump

```
I need to braindump
```

Share whatever's on your mind - messy is fine. The AI organizes themes, extracts action
items, and files everything correctly.

### Get Your First Daily Brief

```
Give me my daily brief
```

The AI finds recent news matching your interests, verifies sources, and saves a briefing
to `01-daily/briefs/`.

---

## 4. Daily Cheat Sheet

| When | Type | What happens |
|---|---|---|
| **Morning** | "Give me my daily brief" | Personalized news based on your interests |
| **Anytime** | "I need to braindump" | Captures thoughts, extracts action items |
| **Found a link** | "Save this URL: …" | Extracts content with key insights |
| **After real work** | "Log this to my journal" | Short dated entry in your work journal, written for you |
| **Friday** | "Weekly review" | Pattern analysis across your week |
| **Monthly** | "Consolidate my knowledge" | Builds frameworks from scattered notes |
| **Overdue to-dos** | "What's overdue?" | Sorts through your task list with you |

**Beyond chat** - things Gemini Scribe adds that are worth knowing about:

- **Right-click selected text** → Rewrite, Explain, or Ask a question about it
- **Summarize a note** - command palette → "Summarize active file", drops a one-line
  summary into the note's frontmatter
- **Autocomplete** - suggestions appear as you type; `Tab` accepts, any other key
  dismisses
- **Ask by meaning** - "what did I write about the school project?" works even if you
  never used those exact words

**Tips:**

- **Be natural.** "I have some thoughts" works as well as "braindump".
- **Braindump often.** More input = better weekly reviews.
- **Don't worry about organization.** The AI files everything.
- **You don't need to attach files.** The assistant searches and reads the vault by
  itself. Attaching is only for pinning something you'll refer to repeatedly.

---

## 5. Working With Context

"Context" is what the assistant is currently holding in its head. Two things to know:

**Starting fresh.** Long conversations get expensive and muddled. When you switch to a
new topic, start a new session: command palette → **"New agent session"**. Old sessions
are saved under `gemini-scribe/Agent-Sessions/` and you can reopen them with
**"Browse agent sessions"**.

**Pinning a file.** Type `@` and pick a note to keep it in front of the assistant for
the whole session. Pinned files show in the strip above the input box - click the `×`
to unpin. Use this for a document you're actively working on. For everything else, just
ask; the assistant will find it.

There is a token counter under the input. Green is fine. When it turns orange or red the
conversation is getting long - that's a good moment to start a new session.

---

## 6. Updating COG

When Gusta releases new COG features:

1. Open your `cog-second-brain` folder in File Explorer
2. Double-click `cog-update.bat`
3. Wait for **"COG updated successfully"**

The script runs `git pull` to fetch the latest framework, including updated skills. If
it reports a problem (usually because the update touches a file you've also edited
locally), **don't panic** - your notes are safe on disk. Ask Gusta to resolve.

**The plugins update separately.** `cog-update.bat` only updates COG itself. Obsidian
tells you when Gemini Scribe or the others have a new version: Settings → **Community
plugins** → **Check for updates** → **Update all**. Nothing breaks if you never do it,
you just miss new plugin features.

Re-running `cog-install.ps1` also refreshes all four plugins to their latest release.
It skips whatever is already in place, so it is a safe repair step at any time.

---

## 7. Troubleshooting

### "The install script failed"

- **"winget is missing"** - install **App Installer** from the Microsoft Store, then
  re-run the one-liner.
- **"OneDrive folder not found"** - sign in to OneDrive first. The script needs the
  folder to exist before it clones into it.
- **Anything else** - the script is safe to re-run; it skips whatever already worked.
  If it still fails, use the manual install in [Step 1](#step-1-run-the-installer).

### "I don't see the COG skills when I type /"

- Settings → Gemini Scribe → General → **Plugin state folder** must be `gemini-scribe`
- Check the folder `gemini-scribe/Skills/` exists in your vault. If it doesn't, run
  `cog-update.bat`.

### "The AI doesn't know about COG"

- Check that `gemini-scribe/AGENTS.md` exists. If it doesn't, run `cog-update.bat`.
- Don't click "Initialize vault context" - that replaces it with a generic version.

### "I got a rate limit error"

- Wait a minute and try again
- Or switch model: Settings → Gemini Scribe → Chat model → `gemini-2.5-flash`
- Or ask Gusta to check the Google AI Studio quota

### "My daily brief has no news"

- Check your internet connection
- Verify `00-inbox/MY-INTERESTS.md` has topics listed

### "I want to change my interests"

- Open `00-inbox/MY-INTERESTS.md` in Obsidian and edit it
- Or tell the AI: "Update my interests - I'm also interested in photography"

### "The AI changed a note and I didn't want it to"

- `Ctrl+Z` in the note usually undoes it
- Turn on confirmations: Settings → Gemini Scribe → **Tool permissions** → enable
  `write_file` and `delete_file`. You'll get an approve/reject prompt before each change.
- Deletions follow your Obsidian "Deleted files" setting, so they land in `.trash` or the
  system trash rather than disappearing

### "Mobile sync isn't working"

- **Tap the sync button** in Remotely Save manually - there's no background sync
- Check both devices use the same Microsoft account
- Check the vault name matches (`cog-second-brain`) on both devices
- OneDrive Personal only - not OneDrive for Business

### "I accidentally deleted a file"

- OneDrive keeps 30-day file history - log into onedrive.live.com and restore
- Or ask Gusta (git history can also recover framework files)

---

## 8. Migrating from OpenCode

If you were set up before July 2026, you had OpenCode - a chat interface in a browser
tab, started from a black terminal window. Here's how to move.

**Your notes are unaffected.** Everything in `00-inbox/`, `01-daily/`, `02-personal/`
and the rest stays exactly where it is. Only the tool you talk to changes.

1. **Update the vault** - double-click `cog-update.bat`. This brings in
   `gemini-scribe/Skills/` and `gemini-scribe/AGENTS.md`.
2. **Install and configure Gemini Scribe** - follow [Steps 2-4](#2-one-time-setup)
   above. Reuse your existing API key; it's the same Google key.
3. **Delete the desktop shortcut** - `opencode-cog.bat`. You don't need it.
4. **Uninstall OpenCode** (optional) - `winget uninstall SST.OpenCodeDesktop`.
5. **Remove the old Obsidian plugin** if you had one - Settings → Community plugins →
   disable and remove **Claudian** and/or **OpenCode Obsidian**. Gemini Scribe replaces
   both. Keep Claudian only if you are deliberately staying on Claude - see
   [If the model has to be Claude](#if-the-model-has-to-be-claude-use-claudian).

**What's different day to day:**

| Before (OpenCode) | Now (Gemini Scribe) |
|---|---|
| Double-click a `.bat`, wait for a browser tab | Click ✨ in Obsidian |
| Terminal window must stay open | Nothing to keep open |
| Chat only | Chat + right-click rewrite + autocomplete + summaries |
| Desktop only | Desktop and phone |
| `/braindump` typed as a command | Same, or just say "I need to braindump" |

**What you lose:** nothing you were using. All 15 COG skills carry over.

---

## 9. Models & Alternatives

### Switching models

Settings → Gemini Scribe → **General**. Separate models can be set for chat,
summarization and autocomplete.

| Model | Best for |
|---|---|
| `gemini-3-flash-preview` | **Recommended.** Best balance of speed, quality, price. |
| `gemini-2.5-flash` | Stable fallback if Gemini 3 misbehaves. |
| `gemini-2.5-pro` | Higher quality, costs more. |

### Why Google AI Studio?

Direct API access, no platform fee, you pay only for tokens used.

### Alternatives (for reference)

Gemini Scribe now speaks to **three** providers - Google Gemini, Ollama (local), and
OpenAI, the last of which also covers any OpenAI-compatible server such as LM Studio.
So switching away from Google AI Studio no longer means switching plugin, unless the
model has to be Claude.

| Alternative | Plugin | Trade-off |
|---|---|---|
| **OpenAI** | Gemini Scribe | Just a provider switch and an OpenAI key; API-key billing only, no ChatGPT-subscription login |
| **Ollama (local)** | Gemini Scribe | Free and private; needs a powerful PC |
| **Claude, Grok, others** | **Claudian** | Wider model choice; requires a command-line tool installed on every machine (see below) |
| **Any ACP agent** | **Agent Client** | Same idea, built on the open Agent Client Protocol; younger project (v0.11.0) |

**You don't have to move everything at once.** Settings → Gemini Scribe →
**Per-feature provider** routes each capability separately, so chat can run locally on
Ollama while Google still serves the tools only it has:

| Feature | Gemini | Ollama | OpenAI |
|---|:---:|:---:|:---:|
| Chat, agent sessions, scheduled tasks | ✓ | ✓ | ✓ |
| Summaries, completions, rewrite | ✓ | ✓ | ✓ |
| Google Search, web fetch, Deep Research | ✓ | ✗ | ✗ |
| Vault semantic search (RAG) | ✓ | ✗ | ✗ |
| Image generation | ✓ | ✗ | ✗ |

Two things worth knowing before mixing providers:

- **Nothing goes to the cloud on your behalf.** If your provider can't serve a feature,
  that feature stays off - the plugin never quietly substitutes another one.
- **Vault semantic search is the broad one.** Turning it on uploads note content to a
  cloud index, not just the text of a single request.

### If the model has to be Claude: use Claudian

**[Claudian](https://community.obsidian.md/plugins/realclaudian)** is the plugin to
switch to for models Gemini Scribe cannot reach. It is the most widely used AI plugin in
the Obsidian ecosystem, and it does the same job as Gemini Scribe - a chat sidebar with
your vault as the working directory, file read/write, search, inline edit with diff
preview, Plan Mode, and multi-tab conversations.

**When it's the right call:**

- The model has to be Claude, Grok, or anything OpenCode or Pi can reach. **GPT no
  longer belongs on this list** - Gemini Scribe has a native OpenAI provider.
- You want one plugin that follows you across providers instead of one plugin per vendor

**What it needs that Gemini Scribe doesn't:**

- A **command-line agent installed and logged in** on every machine - Claude Code,
  Codex CLI, Grok Build, OpenCode, or Pi. That's a terminal install plus an auth step
  per person, per device.
- **Desktop only.** No iOS or Android; the plugin drives a local process and phones
  can't run one. Mobile would go back to read-only.
- Obsidian v1.7.2 or newer.

**One genuine advantage:** Claudian reads skills straight from `.agents/skills/`, which
is where COG already keeps them. The `gemini-scribe/Skills/` copy exists only because
Gemini Scribe can't see into dot-folders - with Claudian that mirror is unnecessary and
skills work with no extra step.

**Known rough edges** (as of July 2026, from the plugin's issue tracker):

- Windows setups regularly fail with `Claude Code process exited with code 1` even when
  the same CLI works fine in a terminal - usually a `PATH` or environment-variable
  problem that Obsidian can't see
- Obsidian can freeze for a minute or more during very long responses, and
  [one report of it hanging after extended sessions](https://github.com/YishenTu/claudian/issues/538)
  is still open
- The plugin can break when the underlying CLI updates independently of it

None of these are dealbreakers for a technical user, but they are the reason Gemini
Scribe is the default for the family: it has no CLI to go wrong.

> If Claudian misbehaves specifically on its OpenCode backend, the older
> `mtymek/opencode-obsidian` plugin still works, installed via the **BRAT** plugin.

---

## Your COG Folder Structure

```
cog-second-brain/
  .git                  Small pointer file - DON'T DELETE
  BFU-SETUP.md          This guide
  cog-install.ps1       One-time setup script (Gusta runs this)
  cog-update.bat        Double-click to update COG
  00-inbox/             Your profile and settings
    MY-PROFILE.md         your name, role, projects
    MY-INTERESTS.md       topics for daily briefs
  01-daily/             Daily outputs
    briefs/                morning news briefings
    checkins/              weekly reflections
  02-personal/          Personal thoughts (braindumps)
  03-professional/      Work/school-related
  04-projects/          Project-specific notes
  05-knowledge/         Consolidated insights
    consolidated/          frameworks from your notes
    patterns/              patterns the AI discovered
    booklets/              saved URLs and articles
  06-templates/         Markdown templates
  gemini-scribe/        AI assistant's folder
    AGENTS.md             how the AI understands your vault
    Skills/               the COG skills
    Agent-Sessions/       your saved conversations
```

Everything is plain text. Open any file with Notepad, Obsidian, or any text editor.

---

## Privacy & Safety

- All notes stay on YOUR computer + YOUR OneDrive
- Requests go from your machine straight to Google's API - no third-party server in
  between, and your data is not used for model training on the paid tier
- Conversations are saved in your vault as markdown, so you can read and delete them
- Attached files are sent to Google for analysis - don't attach anything you wouldn't
  want processed
- For maximum privacy: ask Gusta about Ollama (local models, requires a powerful PC)

---

## Quick Reference Card

Print this and keep it near your computer:

```
START:      Open Obsidian, click the sparkles icon
NEW TOPIC:  Ctrl+P -> "New agent session"

BRAINDUMP:  "I need to braindump"
NEWS:       "Give me my daily brief"
SAVE LINK:  "Save this URL: [paste link]"
WEEKLY:     "Weekly review"
MONTHLY:    "Consolidate my knowledge"

PIN A NOTE: type @ then pick the note
UPDATE COG: Double-click cog-update.bat
PHONE:      Open Obsidian -> tap Remotely Save sync

PROBLEMS:   Ask Gusta!
```

---

*Setup guide v4 - August 2026 (Gusta)*
