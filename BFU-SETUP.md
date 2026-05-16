---
type: guide
created: 2026-02-23
updated: 2026-05-16
status: active
audience: family
---

# COG Family Setup Guide

Step-by-step guide to set up your AI-powered second brain.

**What is COG?** A system that helps you capture thoughts, get personalized news, reflect on your week, and build knowledge over time. Everything is stored as text files on your computer — private, yours.

**What is OpenCode?** A free AI assistant that runs in your browser. You chat with it, and it reads/writes your COG files.

**What changed (May 2026):**

- Vault lives in your **OneDrive folder** — your notes sync to your phone automatically.
- **Claudian** is the recommended Obsidian sidebar plugin (replaces OpenCode Obsidian).
- Mobile read access via **Obsidian + Remotely Save** plugin.
- Optional mobile AI via the **Gemini Scribe** plugin (read-only, ask-mode over your vault).
- Updates are now a double-click: `cog-update.bat`.

---

## Table of Contents

1. [Quick Overview](#1-quick-overview)
2. [One-Time Setup (Gusta does this)](#2-one-time-setup)
3. [Your First Time Using COG](#3-your-first-time-using-cog)
4. [Daily Cheat Sheet](#4-daily-cheat-sheet)
5. [Updating COG](#5-updating-cog)
6. [Troubleshooting](#6-troubleshooting)
7. [Model Recommendations & Alternatives](#7-model-recommendations--alternatives)

---

## 1. Quick Overview

COG uses **Google AI Studio** with **Gemini 3 Flash** — fast and affordable. Gusta creates an API key linked to billing. Each family member gets their own key.

**Costs:**

| Usage Level | Estimated Cost | Notes |
|---|---|---|
| Light (a few sessions/week) | ~$0.10–0.30/mo | Most family members |
| Daily (brief + braindump every day) | ~$0.30–1/mo | Active users |
| Heavy (multiple long sessions/day) | ~$1–3/mo | Power users |

Gemini 3 Flash: **$0.50/1M input tokens**, **$3/1M output tokens**. A typical COG session costs less than $0.01. **Gusta manages billing.**

**Sync architecture:**

- Vault lives in your **OneDrive folder** on your desktop
- OneDrive auto-syncs across all your desktops on the same Microsoft account
- On Android/iOS, the **Remotely Save** Obsidian plugin pulls the vault on demand

---

## 2. One-Time Setup

> Gusta does this for each family member's desktop. You don't do this yourself.

### Step 1: Install OpenCode

```
winget install SST.OpenCodeDesktop
```

Or download from https://opencode.ai/download.

### Step 2: Install the COG Vault into OneDrive

Open PowerShell and run these two lines:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.cog-git" | Out-Null
git clone -b feature/custom-changes git@github.com:gius/COG-second-brain.git `
  --separate-git-dir="$env:USERPROFILE\.cog-git\cog.git" `
  "$env:USERPROFILE\OneDrive\cog-second-brain"
```

The first line creates the parent directory for the git database (git won't auto-create it). The second clones Gusta's family COG fork (the `feature/custom-changes` branch). Requires an SSH key on this machine that's registered with the `gius` GitHub account.

**What this does:**

- Vault content goes into `OneDrive\cog-second-brain` — OneDrive auto-syncs it to your phone and other desktops.
- The git database lives at `~\.cog-git\cog.git` — **outside** OneDrive, so OneDrive doesn't try to sync git's thousands of tiny internal files (that would be slow and break the repo).
- A tiny `.git` pointer file remains inside the OneDrive folder. **Don't delete it** — it's how `cog-update.bat` finds the git data.

### Step 3: Connect to Google AI Studio

Gusta creates an API key at https://aistudio.google.com and links it to billing.

**3a. Authenticate OpenCode:**

```powershell
cd "$env:USERPROFILE\OneDrive\cog-second-brain"
opencode auth login
```

- Select **Google**
- Paste the API key Gusta provides
- Done

**3b. Pick a model:**

In OpenCode, run `/models`:

| Model | Input / 1M | Output / 1M | Best For |
|---|---|---|---|
| `gemini-3-flash-preview` | $0.50 | $3.00 | **Recommended.** Best balance of speed, quality, price. |
| `gemini-2.5-flash` | $0.30 | $2.50 | Stable fallback. |
| `gemini-2.5-pro` | $1.25 | $10.00 | Higher quality, costs more. |

**Recommended thinking level:** `medium`.

### Step 4: Desktop Shortcut

Create `opencode-cog.bat` on the desktop:

```batch
@echo off
cd /d %USERPROFILE%\OneDrive\cog-second-brain
opencode web --port 4000
```

Double-clicking opens COG at http://localhost:4000.

### Step 5: Install Obsidian (Recommended)

Obsidian gives you a visual interface to browse and edit notes.

1. Download from https://obsidian.md (free)
2. Open Obsidian → **Open folder as vault**
3. Select `%USERPROFILE%\OneDrive\cog-second-brain`
4. Install these Community plugins (Settings → Community plugins → Browse):

| Plugin | What it does |
|---|---|
| **Tasks** | Track to-dos with due dates across all your notes |
| **Calendar** | Visual calendar sidebar |
| **Claudian** | AI assistant inside Obsidian — auto-injects vault context, inline diffs, Plan Mode |
| **Remotely Save** | Mobile-friendly sync via OneDrive (see Step 6) |

> **About Claudian:** It's Claude-Code-first; OpenCode backend support is still maturing. If a feature feels broken, fall back to `mtymek/opencode-obsidian` via the **BRAT** plugin.

### Step 6: Mobile Setup (Phone/Tablet)

#### Vault sync via OneDrive

1. On Android/iOS, install **Obsidian** from the app store (free)
2. Create a new vault with the **same name** as your desktop vault: `cog-second-brain`
3. Install **Community plugins → Browse → "Remotely Save"**
4. In Remotely Save settings:
   - Remote Service: **OneDrive**
   - Click **Auth**, log in with the same Microsoft account as desktop
   - Tap the sync arrow in the sidebar for the first sync

**Important caveats:**

- Works with **OneDrive Personal** only — NOT OneDrive for Business
- **No background sync** — you must open Obsidian and tap sync (or enable Scheduled Sync, which runs only while Obsidian is open)
- First sync can take a while on a slow connection

#### Mobile AI (optional, ask-mode only)

If you want to chat with your vault from your phone:

1. In Obsidian mobile, install **Community plugins → Browse → "Gemini Scribe"**
2. Settings:
   - Paste your Gemini API key (same key as desktop OpenCode)
   - **Permission preset: Read Only** — keeps mobile to ask-mode so you can't accidentally edit/delete notes
3. Open the Gemini Scribe chat panel and ask things like *"what did I note about X?"*

Gemini Scribe works on iOS and Android. It can search and summarize your vault — but cannot run COG skills like `/braindump` or `/daily-brief`. Those still need desktop OpenCode.

---

## 3. Your First Time Using COG

### Starting OpenCode

1. Double-click `opencode-cog` on your desktop
2. A browser tab opens with a chat interface
3. You're ready

### Run Onboarding

Type:

```
Run onboarding
```

Answer naturally:

> "I'm Jana, a student interested in biology, art, and sustainability. I'm working on a school project about local ecosystems."

The AI creates:

- `00-inbox/MY-PROFILE.md`
- `00-inbox/MY-INTERESTS.md`
- Project folders in `04-projects/` (if mentioned)

Takes about 2 minutes.

### Try Your First Braindump

```
I need to braindump
```

Share whatever's on your mind — messy is fine. The AI organizes themes, extracts action items, files everything correctly.

### Get Your First Daily Brief

```
Give me my daily brief
```

The AI finds recent news matching your interests, verifies sources, and saves a personalized briefing to `01-daily/briefs/`.

---

## 4. Daily Cheat Sheet

| When | Type | What happens |
|---|---|---|
| **Morning** | "Give me my daily brief" | Personalized news based on your interests |
| **Anytime** | "I need to braindump" | Captures thoughts, extracts action items |
| **Found a link** | "Save this URL: …" | Extracts content with key insights |
| **Friday** | "Weekly review" | Pattern analysis across your week |
| **Monthly** | "Consolidate my knowledge" | Builds frameworks from scattered notes |
| **On phone** | Open Obsidian → Gemini Scribe chat panel | Read-only ask-mode over your vault |

**Tips:**

- **Be natural.** "I have some thoughts" works as well as "/braindump".
- **Braindump often.** More input = better weekly reviews.
- **Don't worry about organization.** The AI files everything.
- **Phone = quick capture and ask-mode.** AI workflows happen at the desktop.

---

## 5. Updating COG

When Gusta releases new COG features:

1. Open your `cog-second-brain` folder in File Explorer
2. Double-click `cog-update.bat`
3. Wait for **"COG updated successfully"**

The script runs `git pull` to fetch the latest framework. If it reports a problem (usually because the framework update touches a file you've also edited locally), **don't panic** — your notes are safe on disk. Ask Gusta to resolve.

---

## 6. Troubleshooting

### "The browser page won't load"

- Make sure the terminal window (the black box) is still running. Don't close it.
- Refresh the browser.
- If the terminal closed, double-click the shortcut again.

### "The AI doesn't know about COG"

- Make sure OpenCode was started from inside your COG folder (the shortcut handles this)
- Type: "Read the AGENTS.md file and follow its instructions"

### "I got a rate limit error"

- Wait a minute and try again
- Or switch model: type `/models` and pick `gemini-2.5-flash`
- Or ask Gusta to check Google AI Studio quotas

### "My daily brief has no news"

- Check internet connection
- Verify `00-inbox/MY-INTERESTS.md` has topics listed

### "I want to change my interests"

- Open `00-inbox/MY-INTERESTS.md` in any text editor
- Or tell the AI: "Update my interests — I'm also interested in photography"

### "Mobile sync isn't working"

- **Tap the sync button** in Remotely Save manually — there's no background sync
- Check both devices use the same Microsoft account
- Check the vault name matches (`cog-second-brain`) on both devices
- OneDrive Personal only — not OneDrive for Business

### "I accidentally deleted a file"

- OneDrive keeps 30-day file history — log into onedrive.live.com and restore from there
- Or ask Gusta (git history can also recover framework files)

---

## 7. Model Recommendations & Alternatives

### Switching Models

Type `/models` in OpenCode anytime.

**Recommended:**

- `gemini-3-flash-preview` — newest, best value, thinking capability
- `gemini-2.5-flash` — stable fallback if Gemini 3 has issues

**Thinking levels:**

- `low` — fast, cheap, simple braindumps
- `medium` — balanced, recommended for most tasks
- `high` — deepest reasoning, best for weekly reviews and consolidation

### Why Google AI Studio?

Direct API access, no platform fee, you pay only for tokens. For COG workloads, Gemini 3 Flash gives the best value: fast, capable, very cheap.

### Alternatives (for reference)

If Google AI Studio ever becomes unsuitable, Gusta can switch to:

| Alternative | Fee | Models | Pros | Cons |
|---|---|---|---|---|
| **OpenRouter** | 5.5% markup | 400+ (all providers) | One key for Claude, GPT, Gemini | 5.5% platform fee |
| **Anthropic** | 0% | Claude only | Best quality models | More expensive |
| **DeepSeek** | 0% | DeepSeek only | Extremely cheap | Single provider |

Switching providers is transparent — Gusta updates config, you keep using OpenCode the same way.

---

## Your COG Folder Structure

```
cog-second-brain/
  .git                  Small pointer file — DON'T DELETE
  BFU-SETUP.md          This guide
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
```

Everything is plain text. Open any file with Notepad, Obsidian, or any text editor.

---

## Privacy & Safety

- All notes stay on YOUR computer + YOUR OneDrive
- Google processes AI requests via API — your data is not used for model training on the paid tier
- You can delete any file at any time
- For maximum privacy: ask Gusta about local AI models (requires a powerful computer)

---

## Quick Reference Card

Print this and keep it near your computer:

```
START:      Double-click "opencode-cog" on desktop
            (or open browser to localhost:4000)

BRAINDUMP:  "I need to braindump"
NEWS:       "Give me my daily brief"
SAVE LINK:  "Save this URL: [paste link]"
WEEKLY:     "Weekly review"
MONTHLY:    "Consolidate my knowledge"

UPDATE COG: Double-click cog-update.bat
PHONE:      Open Obsidian → tap Remotely Save sync

PROBLEMS:   Ask Gusta!
```

---

*Setup guide v2 — May 2026 (Gusta)*

## Related Research

- [[llm-providers-ai-clients-family-cog-2026-02-23|LLM Providers & Clients for Family COG (Feb 2026)]]
