# Output Styles

Two writing styles that replace the agent's default response voice. Source of truth - `cog-sync.sh` copies these into `.claude/output-styles/`, where Claude Code picks them up. Do not edit the generated copies.

| Style | Shape | Use when |
|---|---|---|
| `pyramid` | Bottom line, then reasons, then evidence. Layered so you can stop reading at any depth. | Reviews, investigations, decisions, anything where the reasoning matters as much as the answer |
| `terse` | Bottom line, then what changed and what is next. Three lines beat ten. | Status checks, quick questions, sessions where you already hold the context |

Both share the same marker vocabulary (🎯 ✅ ❌ ⚠️ 🔍 ⏭️) and the same bullet grammar, so switching between them does not change how a response reads - only how deep it goes.

## Using them

In Claude Code: `/output-style pyramid` or `/output-style terse`.

Both set `keep-coding-instructions: true`, so they change how the agent writes without dropping the harness's engineering behaviour.

## Depth triggers

Neither style can be changed mid-turn by the reader, so both respond to in-band words instead. Say `short`, `just the answer`, `expand`, `why`, or `show me` and the depth changes for that answer.

## Other runtimes

Output styles are a Claude Code feature. On runtimes without it, paste the body of the style file into your system prompt or agent instructions - the content has no tool-specific dependencies.
