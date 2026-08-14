---
name: meeting-transcript
description: Process meeting recordings and notes into structured decisions, action items, and team dynamics with intelligent noise filtering
metadata:
  roles: product-manager,engineering-lead,founder,designer
  keywords: process meeting,meeting notes,meeting transcript,extract action items,meeting
  display-name: COG Meeting Transcript
---

# COG Meeting Transcript Skill

## When to Invoke
- User shares a meeting transcript or recording notes
- User says "process meeting", "meeting notes", "meeting transcript"
- User has a block of text from a meeting they want structured
- User mentions wanting to extract action items from a meeting

## Agent Mode Awareness

**Delegation buckets** (`agent_mode: team` only — mode check and tier rules in `AGENTS.md → Model Tiers`): only for transcripts over ~2000 words. Below that, process sequentially in main context — the spawn cost outweighs the benefit on a short transcript. At most 3 **specialist-tier** sub-agents, ≤3KB output each:

1. **Content extraction** (always) — decisions with rationale, action items with owners and deadlines, strategic themes, key quotes, unresolved issues.
2. **Team dynamics** (skip for solo standups) — participation, collaboration quality, decision-making effectiveness, tensions and alignment issues.
3. **Context enrichment** (skip when there is no project hint and no watchlist match) — connections to recent braindumps, existing strategic priorities, competitive intelligence.

Filtering judgment, assembly against the Content Structure template, and flagging urgent action items happen in main context.

## Purpose
Extract strategic insights from meeting recordings and notes with intelligent content filtering to focus on substantive, actionable content while removing noise and irrelevant information.

## Command: `/meeting-transcript`

## Content Filtering Guidelines

### EXCLUDE (Filter Out)
- **Side Conversations**: "Hey, did you see the game last night?"
- **Technical Difficulties**: "Can you hear me now?" "Your mic is muted"
- **Incomplete Thoughts**: "So I was thinking we should... never mind"
- **Casual Banter**: Weather, personal anecdotes unrelated to work
- **Interruptions**: "Sorry, I have to take this call"
- **Unclear Statements**: Mumbled or inaudible content

### INCLUDE (Keep and Analyze)
- **Strategic Discussions**: Market analysis, competitive positioning
- **Decision Points**: "We've decided to move forward with Option A"
- **Action Items**: "Alex will complete the analysis by Friday"
- **Problem Solving**: Discussion of challenges and proposed solutions
- **Planning**: Timeline discussions, resource allocation
- **Insights**: "The key insight is that customers want..."
- **Concerns**: "My concern is that this approach might..."

## Metadata Template
```yaml
type: meeting-transcript
domain: [personal|professional|project-specific]
project: [project-name] # Only for project-specific meetings
date: YYYY-MM-DD
created: YYYY-MM-DD HH:MM
meeting_type: [1-on-1|team-meeting|strategic-planning|project-review|other]
participants: [participant1, participant2, participant3]
duration: [minutes]
content_filtered: true
accuracy_verified: [true|false|pending]
action_items_count: [number]
decisions_count: [number]
tags:
  - meeting
  - transcript
  - domain-tag
  - project-tag
status: [processed|needs-follow-up|action-required]
```

## Content Structure

### 1. Meeting Overview
- **Date/Time**: When the meeting occurred
- **Participants**: Who was present and their roles
- **Purpose**: Primary objective of the meeting
- **Duration**: Actual meeting length
- **Type**: Category of meeting

### 2. Key Decisions (Verified Content Only)
- **Decision**: What was decided
- **Rationale**: Why this decision was made
- **Owner**: Who is responsible for implementation
- **Timeline**: When decision takes effect
- **Impact**: Expected outcomes and implications

### 3. Action Items (Substantive Only)
- **Task**: Specific action to be taken
- **Owner**: Person responsible
- **Deadline**: When it's due
- **Dependencies**: What needs to happen first
- **Success Criteria**: How completion will be measured

### 4. Strategic Themes (From Substantial Discussion)
- **Theme**: Major topic or pattern discussed
- **Context**: Why this theme is important
- **Implications**: What this means for the team/project
- **Next Steps**: How to address or leverage this theme

### 5. Unresolved Issues
- **Issue**: Problem or question that remains open
- **Context**: Background and importance
- **Blocking Factors**: What's preventing resolution
- **Proposed Next Steps**: How to move forward

### 6. Team Dynamics Assessment
- **Communication Quality**: How effectively team communicated
- **Decision-Making Process**: How decisions were reached
- **Participation**: Who contributed and how
- **Meeting Efficiency**: Time management and focus
- **Areas for Improvement**: Suggestions for better meetings

### 7. People Observations (offer, never automatic)
After the meeting note is written, list the per-person observations worth keeping - role or ownership changes, working style, collaboration patterns, decisions they drove. Offer to append them to `05-knowledge/people/` via `/people`, citing this meeting note as the source. Apply that skill's neutrality rule before offering: anything you would not show the person themselves does not make the list. If the user declines, drop them - do not write profiles silently.

## Domain-Specific Processing

### Personal Domain Meetings
- Focus on career development and personal growth
- Maintain strict privacy for personal discussions
- Extract learning and development opportunities
- Save to `[CUSTOMIZE: path/to/personal/]meetings/`

### Professional Domain Meetings
- Analyze leadership and team management aspects
- Extract strategic business insights
- Identify professional development opportunities
- Save to `[CUSTOMIZE: path/to/professional/]meetings/`

### Project-Specific Meetings
- Connect to project metrics and milestones
- Analyze progress against project goals
- Extract competitive and market intelligence
- Save to `[CUSTOMIZE: path/to/projects/][project-name]/meetings/`

## Content Filtering Protocol

### Step 1: Initial Scan
- Identify meeting phases (intro, main discussion, wrap-up)
- Mark obvious side conversations and technical issues
- Flag incomplete or unclear statements

### Step 2: Relevance Assessment
- Evaluate each segment for strategic value
- Determine if content relates to meeting objectives
- Assess completeness and accuracy of information

### Step 3: Accuracy Verification
- Cross-check contradictory statements
- Flag information that seems incorrect
- Note areas requiring clarification

### Step 4: Context Preservation
- Ensure decisions have sufficient context
- Maintain background for action items
- Preserve strategic discussion flow

## Quality Assurance

### Verification Standards
- All decisions must have clear context and rationale
- Action items must have specific owners and deadlines
- Strategic themes must be supported by substantial discussion
- Team dynamics assessment must be based on observable patterns

### Uncertainty Handling
- Flag potentially incorrect information for user confirmation
- State confidence levels for interpretations
- Request clarification for ambiguous content
- Explicitly note when information is incomplete

## What Good Looks Like

A successful meeting processing means: all decisions have clear context and rationale, action items have specific owners and deadlines, and noise is filtered without losing nuance.

