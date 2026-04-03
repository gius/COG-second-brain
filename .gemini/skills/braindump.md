
# COG Braindump Skill

## Purpose
Transform raw thoughts into strategic intelligence through quick capture, systematic analysis, pattern recognition, and domain-aware insight extraction with minimal user friction.

## When to Invoke
- User wants to capture stream-of-consciousness thoughts
- User says "braindump", "brain dump", "capture thoughts", or "write down ideas"
- User has ideas they want to quickly record
- User mentions wanting to get thoughts out of their head

## Agent Mode Awareness

**Check `agent_mode` in `00-inbox/MY-PROFILE.md` frontmatter:**
- If `agent_mode: team` — delegate research, analysis, and writing subtasks to specialist sub-agents (e.g., use Task tool to delegate deep analysis, competitive intel extraction, or pattern recognition to separate agents). Combine results before presenting to user.
- If `agent_mode: solo` (default) — handle everything directly in the conversation. No delegation.

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
   - Read the profile to get user's name and active projects
   - If user has active projects listed, offer them as domain options
   - Use user's name for friendly communication
   - Read `03-professional/COMPETITIVE-WATCHLIST.md` if it exists for competitive intelligence detection

**Get current timestamp (REQUIRED before generating any files):**

1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
2. Store this value and use it for ALL timestamp fields (`created:` frontmatter AND filename `HHMM` component)
3. NEVER guess or fabricate the time — always use the value returned by the `date` command

## Process Flow

### 1. User Interaction & Input Collection
- Greet user warmly (use their name from MY-PROFILE.md if available)
- Ask: "What's on your mind?" or "Ready for a brain dump?"
- Collect their stream-of-consciousness input (can be long, rambling, voice-to-text, etc.)
- Accept any format - no judgment, no filtering

### 2. Domain Classification
Ask user to classify or auto-detect based on content:

**If user profile exists with projects:**
- **Personal:** Individual growth, relationships, wellness
- **Professional:** Work, leadership, career development
- **Project-Specific:** Related to specific projects
  - If MY-PROFILE.md lists projects, offer: "Which project? [list project names]"
  - Example: "Which project? (1) SaaS Product, (2) Book Writing, (3) Health App"
- **Mixed/Unclear:** Spans multiple areas

**If no profile:** Use standard personal/professional/mixed classification

### 3. Content Analysis and Processing

Apply the comprehensive analysis framework directly:

#### Phase 1: Content Ingestion
Analyze the input to understand:
- **Content Type:** [voice-transcript|written-notes|mixed]
- **Length:** [word-count]
- **Energy Level:** [high|medium|low]
- **Emotional Tone:** [excited|frustrated|curious|concerned|neutral|mixed]
- **Context:** [situational-background]

#### Phase 2: Structural Analysis
Extract and identify:
- **Main Themes:** [3-5 primary topics]
- **Supporting Ideas:** [related concepts and details]
- **Questions Raised:** [explicit and implicit questions]
- **Decisions Contemplated:** [choices being considered]
- **Action Items:** [tasks and commitments identified]

#### Phase 3: Domain Classification (with confidence)
Determine:
- **Primary Domain:** [personal|professional|project-specific] with confidence level
- **Secondary Domains:** [if content spans multiple areas]
- **Cross-Domain Elements:** [themes that apply across domains]
- **Privacy Considerations:** [sensitive content requiring protection]

#### Phase 4: Strategic Insight Extraction
Identify:
- **Key Insights:** [3-5 most important realizations]
- **Pattern Recognition:** [connections to previous thoughts/decisions]
- **Strategic Implications:** [what this means for goals and priorities]
- **Decision Framework:** [how this informs future choices]

#### Phase 5: Competitive Intelligence Detection
If COMPETITIVE-WATCHLIST.md exists:
- Scan braindump content for mentions of tracked companies/people
- Extract competitive intelligence to separate files
- Create cross-references back to original braindump

### 4. Generate Structured Output

Create braindump file with this structure:

```markdown
type: "braindump"
domain: "[personal|professional|project-specific|mixed]"
project: "[project-name]" # Only if project-specific
date: "YYYY-MM-DD"
created: "YYYY-MM-DD HH:MM"
themes: ["theme1", "theme2", "theme3"]
tags: ["#braindump", "#raw-thoughts", "#domain-tag"]
status: "captured"
energy_level: "[high|medium|low]"
emotional_tone: "[primary-emotion]"
confidence: "[high|medium|low]"

# Braindump: [Auto-generated descriptive title]

## Raw Thoughts
[Original user content preserved exactly as provided]

## Content Analysis

### Main Themes
1. **Theme 1:** [description and significance]
2. **Theme 2:** [description and significance]
3. **Theme 3:** [description and significance]

### Supporting Ideas
- [Supporting concept 1]
- [Supporting concept 2]
- [Supporting concept 3]

### Questions Raised
- [Question 1 for deeper exploration]
- [Question 2 requiring consideration]

### Decisions Contemplated
- [Decision 1 being considered with options]
- [Decision 2 under evaluation]

## Strategic Intelligence

### Key Insights
1. **Insight 1:** [description and implications]
2. **Insight 2:** [description and implications]
3. **Insight 3:** [description and implications]

### Pattern Recognition
- **Connection to Previous Thinking:** [links to earlier braindumps or frameworks]
- **Recurring Patterns:** [themes that keep appearing]
- **Evolution:** [how thinking has developed]

### Strategic Implications
- [How this affects goals]
- [Impact on current projects]
- [Decision-making considerations]

## Action Items

**Note:** Calculate actual due dates from today's date and append Obsidian Tasks emoji format.

### Immediate (24-48 hours)
- [ ] [specific action] 📅 [YYYY-MM-DD = tomorrow's date]

### Short-term (1-2 weeks)
- [ ] [specific action] 📅 [YYYY-MM-DD = date +1 week from today]

### Strategic Considerations
- [longer-term implications and considerations]

## Connections
- **Related Braindumps:** [[link1]], [[link2]]
- **Relevant Projects:** [[project1]], [[project2]]
- **Knowledge Base:** [[insight1]], [[framework1]]

## Domain Classification
- **Primary Domain:** [domain] ([confidence]%)
- **Reasoning:** [why this classification]
- **Cross-Domain Elements:** [if applicable]
- **Privacy Level:** [public|private|confidential]

## Processing Notes
### Emotional Context
- **Energy Level:** [assessment]
- **Emotional Tone:** [assessment]
- **Implications:** [what this suggests]

### Confidence Assessment
- **Overall Analysis:** [percentage] - [reasoning]
- **Domain Classification:** [percentage] - [reasoning]
- **Strategic Insights:** [percentage] - [reasoning]
- **Areas Requiring Clarification:** [specific questions if needed]


*Processed by COG Brain Dump Analyst*
```

Save to appropriate location:
- **Personal:** `02-personal/braindumps/braindump-YYYY-MM-DD-HHMM-<slug>.md`
- **Professional:** `03-professional/braindumps/braindump-YYYY-MM-DD-HHMM-<slug>.md`
- **Project:** `04-projects/[project-slug]/braindumps/braindump-YYYY-MM-DD-HHMM-<slug>.md`
- **Mixed:** `00-inbox/braindump-YYYY-MM-DD-HHMM-<slug>.md`

### 5. Competitive Intelligence Extraction

If competitive intelligence detected (mentions of companies/people from watchlist):

Create/update: `04-projects/[project]/competitive/[company-slug].md`

```markdown
type: "competitive-intelligence"
company: "[Company Name]"
project: "[project-name]"
last_updated: "YYYY-MM-DD"
sources: ["braindump"]
tags: ["#competitive", "#intelligence", "#[company-slug]"]

# Competitive Intelligence: [Company Name]

## Latest Update - [Date]
**Source:** [[braindump-file-reference]]

[Extracted competitive intelligence from braindump]

## Previous Intelligence
[Historical intel from earlier braindumps]

## Strategic Implications
[Analysis of what this means for the project]

## Action Items
- [ ] [Follow-up actions based on intel] 📅 [YYYY-MM-DD = calculated due date]


*Auto-extracted by COG Brain Dump Analyst*
```

### 6. Decision Propagation

If the braindump contains **decisions that supersede existing plans or documents**, update those documents in the same session. Braindumps are the historical record (the "why"); plans are the source of truth (the "what"). Both must stay in sync.

**How to detect:**
- Phase 2 "Decisions Contemplated" identified concrete choices (e.g., "use X instead of Y", "drop tool Z", "change approach to coded")
- The braindump's domain/project has existing planning docs, PROJECT-OVERVIEWs, or research files

**When a decision is detected:**
1. Identify which existing documents are affected (check the project's `planning/`, `research/`, and `PROJECT-OVERVIEW.md`)
2. Compare dates — if the planning doc is older, it's stale
3. **Ask the user:** "This braindump changes the plan for [X]. Should I update [list of affected docs] now?"
4. If yes: update the affected documents and add changelog entries with today's date
5. If no: add a note to the braindump's Action Items: `- [ ] Pending: propagate decision to [doc list] 📅 [tomorrow's date]`

**Why this matters:** Without propagation, braindumps and plans diverge. The next person (or AI) reading the plan gets outdated information. The braindump has the truth but isn't the expected place to look for current state.

### 7. Confirm Completion
- Confirm file was created
- Show user: "Braindump saved to [file path]"
- Show quick summary of main themes identified
- If competitive intel extracted, mention: "Also extracted competitive intelligence to [file path]"
- If decision propagation was done, mention: "Updated [N] planning docs to reflect new decisions"

## YAML Formatting Requirements

**CRITICAL:** All YAML frontmatter must use proper Obsidian-compatible formatting:
- All string values MUST be quoted with double quotes
- Arrays MUST use quoted strings: `["item1", "item2", "item3"]`
- Boolean values should NOT be quoted: `true` or `false`
- Numbers should NOT be quoted unless they are string identifiers
- Ensure proper YAML syntax to prevent parsing errors in Obsidian

**Examples:**
```yaml
# CORRECT
type: "braindump"
themes: ["automation", "testing", "ui-improvements"]
analysis_needed: true

# INCORRECT
type: braindump
themes: [automation, testing, ui-improvements]
analysis_needed: "true"
```

## Quality Gates

Before finalizing the braindump output, verify:
- **Domain classification is defensible** — if it could go two ways, ask the user
- **Emotional tone assessment matches content** — don't label frustration as neutral
- **All major themes are captured** — re-read the raw input and check nothing was missed
- **Strategic insights are evidence-based** — supported by what the user actually said, not inferred from thin air

If confidence is below 70%, ask for clarification rather than guessing. State confidence levels in the Processing Notes section: High (90%+), Medium (70-89%), Low (50-69%), Very Low (<50%).

## After Completion

The braindump is a capture point that feeds other skills. After saving, suggest:
- `/weekly-checkin` — to reflect on themes across multiple braindumps
- `/knowledge-consolidation` — if patterns are emerging across several braindumps
- If competitive intel was extracted, mention the competitive intelligence file

## What Good Looks Like

A successful braindump capture means: the user felt heard and unburdened, their raw thoughts are preserved exactly as given, the analysis adds value without distorting meaning, domain classification is correct, and action items are specific with real dates.
