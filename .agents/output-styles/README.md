# Output Styles

One writing style that replaces the agent's default response voice. Source of truth - `cog-sync.sh` copies these into `.claude/output-styles/`, where Claude Code picks them up. Do not edit the generated copies.

| Style | Shape | Use when |
|---|---|---|
| `clear` | Mechanism-first answer line, up to 5 lines of what matters, one drawn shape where the topic has structure. Default is short; `expand`, `why`, `show me`, `draw it` add depth. | Everyday work. The default for a reader who gets lost more often than they want more detail |

Earlier styles `pyramid` and `terse` were folded into `clear` on 2026-09-06: their depth lives behind the `expand` trigger.

## Using them

In Claude Code: set `outputStyle` to `Clear` in `settings.json`; the change applies on a new session or after `/clear`.

It sets `keep-coding-instructions: true`, so it changes how the agent writes without dropping the harness's engineering behaviour.

## Depth triggers

The style cannot be changed mid-session by the reader, so it responds to in-band words instead. Say `just the answer`, `expand`, `why`, `show me`, or `draw it` and the depth changes for that answer.

## Other runtimes

Output styles are a Claude Code feature. On runtimes without it, paste the body of the style file into your system prompt or agent instructions - the content has no tool-specific dependencies.
