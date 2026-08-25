---
type: guide
created: 2026-02-23
updated: 2026-08-25
status: active
audience: family
---

# COG Family Setup Guide

Set up your AI-powered second brain. This is the only setup guide - if you have an
older one saved anywhere, throw it away.

**What is COG?** A system that helps you capture thoughts, get personalized news,
reflect on your week, and build knowledge over time. Everything is stored as text
files on your computer - private, yours.

**You get two assistants, and they are good at different things.**

| | **Claudian** (desktop) | **Gemini Scribe** (phone) |
|---|---|---|
| Where | Obsidian on your PC | Obsidian on your phone or tablet |
| Reads your notes | yes | yes |
| Writes and edits notes | yes | yes |
| Opens files outside the vault | yes - Downloads, Documents, Desktop | no |
| Reads a spreadsheet, runs a calculation, builds a chart | **yes** | no |
| Runs on a schedule, autocompletes as you type | no | yes |
| Default state | **on** | **off** - turn on only if you use the phone |

Claudian is the one you talk to day to day on the computer. Gemini Scribe stays
installed but switched off on the desktop, because two AI assistants in one sidebar is
just confusing. On the phone it is the only one that works, so that is where it earns
its place.

**What changed (August 2026):**

- **Claudian is the new desktop assistant.** It can open a spreadsheet from your
  Downloads folder, do the maths, and hand you back a chart. Gemini Scribe could not do
  any of that - it can only see plain text inside the vault.
- **Gemini Scribe is now the mobile assistant.** Installed but off on the desktop.
- The skills COG ships (`braindump`, `daily-brief`, and the rest) work in both.
- See [Migrating](#8-migrating-from-the-old-setup) if you were set up before this.

---

## Table of Contents

1. [Quick Overview](#1-quick-overview)
2. [One-Time Setup (Gusta does this)](#2-one-time-setup)
3. [Your First Time Using COG](#3-your-first-time-using-cog)
4. [Daily Cheat Sheet](#4-daily-cheat-sheet)
5. [Working With Context](#5-working-with-context)
6. [Updating COG](#6-updating-cog)
7. [Troubleshooting](#7-troubleshooting)
8. [Migrating From the Old Setup](#8-migrating-from-the-old-setup)
9. [Models & Alternatives](#9-models--alternatives)

---

## 1. Quick Overview

Both assistants talk to **Google Gemini Flash** using an API key Gusta creates and pays
for. Same key, same bill as before - only the desktop app around it changed.

**How the desktop one is put together:**

```
You type in Obsidian
   -> Claudian          the chat panel, part of Obsidian
      -> OpenCode       a small program that does the actual work: reads
         |              files, runs commands, writes your notes
         -> Google      Gemini Flash, using Gusta's API key
```

You never see OpenCode. It has no window. Claudian starts it and talks to it for you.

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
- On Android/iOS, the **OneDrive Sync** Obsidian plugin pulls the vault on demand

---

## 2. One-Time Setup

> Gusta does this for each family member's desktop. You don't do this yourself.

### Step 1: Run the installer

Open PowerShell and paste this one line:

```powershell
irm https://raw.githubusercontent.com/gius/COG-second-brain/feature/custom-changes/cog-install.ps1 | iex
```

It installs Git, Obsidian, OpenCode and uv, clones the vault, and downloads the
Obsidian plugins. Every step skips itself if it is already done, so it is safe to
re-run. The script is `cog-install.ps1` in the vault folder if you want to read it
first.

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
| **OpenCode** | `%LOCALAPPDATA%\opencode\opencode.exe`, added to your PATH - the agent behind Claudian |
| **uv** | `winget install astral-sh.uv` - runs Python for spreadsheet and chart work |
| Vault content | `%OneDrive%\cog-second-brain` by default, confirmed on screen first - OneDrive auto-syncs it to your phone and other desktops |
| Git database | `%USERPROFILE%\.cog-git\cog.git` - **outside** OneDrive, so OneDrive doesn't sync git's thousands of tiny internal files (slow, and it breaks the repo) |
| Plugins | Claudian, Tasks, Calendar, Dataview enabled; Gemini Scribe installed but left off |
| Tidying | Excludes `gemini-scribe` from search and the graph - it holds the assistant's own files, not yours |

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
winget install astral-sh.uv
```

Then install OpenCode. Download `opencode-windows-x64.zip` from the
[OpenCode releases page](https://github.com/anomalyco/opencode/releases/latest),
unzip it to `%LOCALAPPDATA%\opencode`, and add that folder to your PATH.

> **Don't install OpenCode with npm.** `npm install -g opencode-ai` gives you a
> `.cmd` wrapper instead of a real `.exe`, and Claudian frequently fails to start it.
> `scoop install opencode` or `choco install opencode` also give you a proper binary
> if you already have one of those.

Then install five plugins from Settings -> **Community plugins** -> **Browse**:
**Claudian**, **Tasks**, **Calendar**, **Dataview**, and **Gemini Scribe** (install
it, then switch it off).

</details>

> **Git is not optional.** `cog-update.bat` runs `git pull`, so a vault downloaded as
> a ZIP instead of cloned can never be updated.

### Step 2: Open the vault

1. Open Obsidian -> **Open folder as vault**
2. Select `%USERPROFILE%\OneDrive\cog-second-brain`
3. Settings -> **Community plugins** -> click **Turn on community plugins** if Obsidian
   asks for it.

| Plugin | State | What it does |
|---|---|---|
| **Claudian** | on | The AI assistant in the side panel |
| **Tasks** | on | Track to-dos with due dates across all your notes |
| **Calendar** | on | Visual calendar sidebar |
| **Dataview** | on | Powers the live queries on `COG-DASHBOARD.md` |
| **Gemini Scribe** | **off** | The phone assistant. Leave it off here |

> Claudian needs **Obsidian 1.13.0 or newer**. If Obsidian was already installed and is
> older, update it: Settings -> **About** -> **Check for updates**.

No sync plugin on the desktop: OneDrive already syncs this folder, and a second
syncer pointed at the same files only creates conflicts. Phones are different - see
Step 5.

### Step 3: Connect the API key

This is the one step that needs a terminal, and it happens once.

1. Open PowerShell
2. Type `opencode` and press Enter
3. Type `/connect` and pick **Google** from the list
4. Paste the API key Gusta made for you

The key is saved in `~/.local/share/opencode/auth.json` and OpenCode uses it from then
on. Press `Ctrl+C` twice to leave.

To check it worked, still in that terminal:

```powershell
opencode run "say hello in five words"
```

If you get a sentence back, the connection is good.

### Step 4: Point Claudian at OpenCode

1. Settings -> **Claudian** -> pick **OpenCode** as the provider
2. Leave the CLI path **empty** - Claudian finds `opencode.exe` on the PATH by itself

To confirm it all works: click the Claudian icon in the left ribbon (or `Ctrl+P` and
type "Claudian") and ask it:

```
What COG skills do you have?
```

It should list `braindump`, `daily-brief`, `weekly-checkin` and the rest.

> **Nothing to configure for skills.** OpenCode reads them straight out of
> `.agents/skills/` in the vault, and reads `AGENTS.md` at the vault root to learn how
> COG is organised. Both ship with the vault.

> **The vault also ships `opencode.json`**, which picks the model and says the assistant
> must ask before running any command. Don't edit it; `cog-update.bat` keeps it current.

### Step 5: Mobile setup (optional)

#### Vault sync

Only phones need a sync plugin. The desktop is already handled by the OneDrive app.

1. On Android/iOS, install **Obsidian** from the app store (free)
2. Create a new vault with the **same name** as your desktop vault: `cog-second-brain`
3. Install **Community plugins -> Browse -> "OneDrive Sync"** -> Enable
4. Settings -> **OneDrive Sync** -> **Access Mode** -> switch to **Full Access**, then
   connect and sign in with the same Microsoft account as the desktop
5. **Set the sync folder to `/cog-second-brain`.** Pick it in the folder picker.
   Do not leave it empty.

> **Why step 5 matters.** In Full Access mode with no folder set, the plugin walks
> your *entire* OneDrive instead of the vault. Setting the folder keeps every sync
> scoped to that one directory. After the first sync, re-open the plugin settings and
> confirm the folder still reads `/cog-second-brain`.

**Caveats:**

- Works with **OneDrive Personal** only - NOT OneDrive for Business
- First sync can take a while on a slow connection
- The phone and desktop share one cloud copy, so a note edited in both places at once
  can conflict. The plugin asks what to keep

#### Mobile AI

**Claudian does not work on phones** - it drives a real program on your computer, and
phones can't run one. Gemini Scribe is the phone assistant.

1. Install **Gemini Scribe** from Community plugins and **enable** it
2. Settings -> Gemini Scribe -> **General** -> Provider `Google Gemini (cloud)`, paste
   the same API key, Chat model `gemini-flash-latest`
3. Settings -> Gemini Scribe -> **General** -> **Plugin state folder** -> pick
   `gemini-scribe`
4. Turn on confirmation for `write_file` and `delete_file` under **Tool permissions**,
   so a mistyped request can't quietly change a note

> Don't click "Initialize vault context" - that overwrites the tuned COG version of
> `gemini-scribe/AGENTS.md` with a generic one.

**On the desktop, leave Gemini Scribe off.** Everything it does, Claudian does, plus
things it can't.

---

## 3. Your First Time Using COG

### Opening the assistant

Click the **Claudian icon** in the left ribbon, or use the command palette (`Ctrl+P`)
and type "Claudian".

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

### Try the thing the phone can't do

Put any spreadsheet in your Downloads folder, then ask:

```
Read C:\Users\jana\Downloads\rozpocet.xlsx, summarize the spending by month,
and make me an HTML chart I can open in a browser.
```

It will write a small Python script, run it, and save an `.html` file you can
double-click. **It will ask permission before running the script** - that prompt is
normal, read it and click approve.

---

## 4. Daily Cheat Sheet

| When | Type | What happens |
|---|---|---|
| **Morning** | "Give me my daily brief" | Personalized news based on your interests |
| **Anytime** | "I need to braindump" | Captures thoughts, extracts action items |
| **Found a link** | "Save this URL: ..." | Extracts content with key insights |
| **After real work** | "Log this to my journal" | Short dated entry in your work journal, written for you |
| **Friday** | "Weekly review" | Pattern analysis across your week |
| **Monthly** | "Consolidate my knowledge" | Builds frameworks from scattered notes |
| **Overdue to-dos** | "What's overdue?" | Sorts through your task list with you |
| **A spreadsheet, a folder of files** | "Read this file and ..." | Opens it, calculates, charts, writes the result into your vault |

**Beyond chat** - things Claudian adds that are worth knowing about:

- **Inline edit** - select text in a note, press the hotkey, and edit it in place with a
  word-by-word preview of what changes
- **Plan mode** - press `Shift+Tab`. The assistant works out what it intends to do and
  shows you the plan before touching anything. Good for a big or scary request
- **`@` a file** - type `@` to point at a note, or a file anywhere on your computer
- **Tabs** - several conversations at once, each on its own topic

**Tips:**

- **Be natural.** "I have some thoughts" works as well as "braindump".
- **Braindump often.** More input = better weekly reviews.
- **Don't worry about organization.** The AI files everything.
- **Read the permission prompts.** When it asks to run something, the command is right
  there in the box. If you don't recognise it, reject it and ask Gusta.

---

## 5. Working With Context

"Context" is what the assistant is currently holding in its head. Two things to know:

**Starting fresh.** Long conversations get expensive and muddled. When you switch to a
new topic, open a new tab in the Claudian panel. Old conversations stay in the session
manager beside the chat.

**Pointing at a file.** Type `@` and pick a note to put it in front of the assistant.
For everything else, just ask - it will find it.

When a conversation starts feeling slow or forgetful, that's the moment to start a new
tab.

---

## 6. Updating COG

When Gusta releases new COG features:

1. Open your `cog-second-brain` folder in File Explorer
2. Double-click `cog-update.bat`
3. Wait for **"COG updated successfully"**

The script runs `git pull` to fetch the latest framework, including updated skills and
`opencode.json`. If it reports a problem (usually because the update touches a file
you've also edited locally), **don't panic** - your notes are safe on disk. Ask Gusta to
resolve.

**Three things update separately:**

| What | How |
|---|---|
| COG itself | `cog-update.bat` |
| Obsidian plugins | Settings -> Community plugins -> Check for updates -> Update all |
| OpenCode | Updates itself - `opencode.json` sets `autoupdate` |

Only the middle row needs you. Nothing breaks if you skip it, you just miss new
plugin features.

---

## 7. Troubleshooting

### "The install script failed"

- **"winget is missing"** - install **App Installer** from the Microsoft Store, then
  re-run the one-liner.
- **"OneDrive folder not found"** - sign in to OneDrive first. The script needs the
  folder to exist before it clones into it.
- **Anything else** - the script is safe to re-run; it skips whatever already worked.
  If it still fails, use the manual install in [Step 1](#step-1-run-the-installer).

### "Claudian says it can't find OpenCode"

This is the most common problem, and it is almost always PATH.

1. Open a **new** PowerShell window and type `opencode --version`. A version number
   means OpenCode is installed and on the PATH.
2. If that works but Claudian still fails, Obsidian was started before the PATH changed.
   **Close Obsidian completely and reopen it.**
3. If it still fails, find the exact path with `where.exe opencode` and paste it into
   Settings -> Claudian -> Advanced -> CLI path. Use the `.exe`, never a `.cmd` file.

### "It asks permission for everything"

That's the safety config doing its job. Reading and writing your notes never asks;
running a program does. Click approve on the ones you asked for.

If it asks about something you did **not** ask for, reject it and tell Gusta.

### "It says it can't open my Excel file"

- On the **phone**, that is expected - Gemini Scribe cannot read spreadsheets. Ask on
  the desktop instead, or save the sheet as CSV and try again.
- On the **desktop**, check the file is in Downloads, Documents or Desktop. Anywhere
  else and the assistant asks permission first - approve the prompt.

### "I don't see the COG skills"

- Ask it directly: "what COG skills do you have?"
- If the list is empty, check `.agents/skills/` exists in the vault. If it doesn't, run
  `cog-update.bat`.

### "I got a rate limit error"

- Wait a minute and try again
- Or ask Gusta to check the Google AI Studio quota

### "My daily brief has no news"

- Check your internet connection
- Verify `00-inbox/MY-INTERESTS.md` has topics listed

### "I want to change my interests"

- Open `00-inbox/MY-INTERESTS.md` in Obsidian and edit it
- Or tell the AI: "Update my interests - I'm also interested in photography"

### "The AI changed a note and I didn't want it to"

- `Ctrl+Z` in the note usually undoes it
- Use **Plan mode** (`Shift+Tab`) for anything big - it shows you the plan first
- Deletions land in `.trash` or the system trash, following your Obsidian "Deleted
  files" setting, rather than disappearing

### "Mobile sync isn't working"

- **Check the sync folder** - Settings -> OneDrive Sync -> it must read `/cog-second-brain`.
  Empty means it is trying to sync your whole OneDrive; set it and sync again
- Check **Access Mode** is **Full Access**, not App Folder
- Check both devices use the same Microsoft account
- OneDrive Personal only - not OneDrive for Business

### "I accidentally deleted a file"

- OneDrive keeps 30-day file history - log into onedrive.live.com and restore
- Or ask Gusta (git history can also recover framework files)

---

## 8. Migrating From the Old Setup

If you were set up before August 2026, Gemini Scribe was your desktop assistant. Here
is how to move.

**Your notes are unaffected.** Everything in `00-inbox/`, `01-daily/`, `02-personal/`
and the rest stays exactly where it is. Only the panel you type into changes.

1. **Update the vault** - double-click `cog-update.bat`. This brings in `opencode.json`
   and the updated guide.
2. **Re-run the installer** - paste the one-liner from
   [Step 1](#step-1-run-the-installer) again. It adds OpenCode, uv and Claudian, and
   skips everything you already have.
3. **Connect the key** - [Step 3](#step-3-connect-the-api-key). It is the same key you
   already have; you are just telling OpenCode about it.
4. **Point Claudian at OpenCode** - [Step 4](#step-4-point-claudian-at-opencode).
5. **Switch Gemini Scribe off on the desktop** - Settings -> Community plugins ->
   toggle it off. Don't uninstall it; your phone still uses it.
6. **Leave your phone alone.** It keeps working exactly as before.

**Your old conversations** stay in `gemini-scribe/Agent-Sessions/` and remain readable
as ordinary notes. Claudian starts with a clean history.

**What's different day to day:**

| Before (Gemini Scribe) | Now (Claudian) |
|---|---|
| Sparkles icon | Claudian icon |
| Vault files only | Vault plus Downloads, Documents, Desktop |
| Could not open a spreadsheet | Opens it, calculates, charts it |
| Never asked before acting | Asks before running a program |
| Autocomplete while typing, scheduled runs | Not available - this is the real loss |

**What you lose:** autocomplete as you type, the automatic note summaries, semantic
"ask by meaning" search, and scheduled tasks. Those were Gemini Scribe features and
have no Claudian equivalent. If you used them daily, tell Gusta - you can run both
plugins side by side, it is only turned off by default to keep things simple.

> Set up before July 2026, with a `.bat` file and a browser tab? That was the original
> OpenCode desktop app. Delete the `opencode-cog.bat` shortcut, run
> `winget uninstall SST.OpenCodeDesktop`, then follow the steps above.

---

## 9. Models & Alternatives

### Switching models

The vault ships `opencode.json` set to `google/gemini-flash-latest`. That is an alias,
not a fixed version - Google points it at whatever the current Flash model is, so the
setup keeps up on its own and nobody edits a config when a new model ships.

To try something else for one conversation, use the model picker in the Claudian input
bar. Pro models cost several times more per message, so don't leave one selected by
accident.

### Why this stack?

- **OpenCode** speaks to 75+ providers, so if Google ever becomes unsuitable, the model
  changes and nothing else does.
- **Claudian** is the most installed AI plugin in Obsidian by a wide margin, which
  matters for a tool the family depends on.
- **OpenCode reads `.agents/skills/` and `AGENTS.md` natively**, which is exactly where
  COG already keeps them. No copies, no sync step, no drift.

### Alternatives (for reference)

| Alternative | How | Trade-off |
|---|---|---|
| **A different model** | `/connect` another provider in OpenCode, change `model` in `opencode.json` | Anything OpenCode supports: Claude, GPT, Grok, local models |
| **Fully local, private** | Run Ollama, point OpenCode at it | Free and nothing leaves the machine; needs a powerful PC and quality drops |
| **Agent Client plugin** | Replaces Claudian, same OpenCode underneath | Adds WSL support and chats embedded in notes; much smaller project |
| **Gemini Scribe on desktop too** | Just switch it on | Gets autocomplete and scheduled tasks back, at the cost of two assistants in one sidebar |

---

## Your COG Folder Structure

```
cog-second-brain/
  .git                  Small pointer file - DON'T DELETE
  AGENTS.md             How the AI understands your vault
  opencode.json         Model and safety rules for the desktop assistant
  BFU-SETUP.md          This guide
  cog-install.ps1       One-time setup script (Gusta runs this)
  cog-update.bat        Double-click to update COG
  .agents/skills/       The COG skills, read by the desktop assistant
  00-inbox/             Your profile and settings
    COG-DASHBOARD.md      live overview of everything in your vault
    TASKS.md              every to-do from every note, in one place
    MY-PROFILE.md         your name, role, projects (created by onboarding)
    MY-INTERESTS.md       topics for daily briefs (created by onboarding)
    MY-INTEGRATIONS.md    which services COG may use (created by onboarding)
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
  gemini-scribe/        The phone assistant's folder (excluded from search)
    AGENTS.md             how the phone assistant understands your vault
    Skills/               a copy of the skills, for the phone
    Agent-Sessions/       saved phone conversations
```

Everything is plain text. Open any file with Notepad, Obsidian, or any text editor.

**Two files you did not write are worth opening on day one:**

- **`00-inbox/COG-DASHBOARD.md`** - counts of your projects, open braindumps and saved
  links, plus tables of everything recent. It builds itself from your notes, so it is
  empty at first and fills as you use COG.
- **`00-inbox/TASKS.md`** - every `- [ ]` from every note, grouped into Overdue, Due
  Today, This Week. Don't type tasks here; write them in the note they belong to and
  they show up automatically.

**Why `gemini-scribe/` looks greyed out.** The installer adds it to Obsidian's
**Excluded files**, so it is hidden from search, the graph and unlinked mentions, and
pushed to the bottom of the quick switcher and link suggestions. The folder still shows
in the file list and you can still open anything in it. To undo: Settings -> **Files and
links** -> **Excluded files**.

---

## Privacy & Safety

- All notes stay on YOUR computer + YOUR OneDrive
- Requests go from your machine straight to Google's API - no third-party server in
  between, and **your data is not used for model training**, because the family key is
  on Google's paid tier. That is a real difference from the free tier, where Google's
  terms allow both training on your content and human review of it
- Conversations are saved in your vault as markdown, so you can read and delete them
- Attached files are sent to Google for analysis - don't attach anything you wouldn't
  want processed
- **The desktop assistant can run programs on your computer.** That is what makes the
  spreadsheet work possible, and it is why it asks permission every single time before
  running anything. The command is shown in the prompt. Read it
- For maximum privacy: ask Gusta about Ollama (local models, requires a powerful PC)

---

## Quick Reference Card

Print this and keep it near your computer:

```
START:      Open Obsidian, click the Claudian icon
NEW TOPIC:  New tab in the Claudian panel
PLAN FIRST: Shift+Tab before a big request

BRAINDUMP:  "I need to braindump"
NEWS:       "Give me my daily brief"
SAVE LINK:  "Save this URL: [paste link]"
WEEKLY:     "Weekly review"
MONTHLY:    "Consolidate my knowledge"
SPREADSHEET:"Read <file> and chart it for me"

POINT AT A FILE: type @ then pick it
UPDATE COG: Double-click cog-update.bat
PHONE:      Obsidian -> Gemini Scribe (Claudian is desktop only)

IF IT ASKS PERMISSION: read the command, approve what you asked for
PROBLEMS:   Ask Gusta!
```

---

*Setup guide v5 - August 2026 (Gusta)*
