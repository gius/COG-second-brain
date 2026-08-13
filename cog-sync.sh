#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# cog-sync.sh — Generate tool-specific files from the single source of truth
# ═══════════════════════════════════════════════════════════════════════
#
# Source of truth:
#   AGENTS.md                    — Framework docs, skill descriptions, vault structure
#   .agents/skills/*/SKILL.md   — Full skill playbooks (agentskills.io standard)
#
# Generated (committed to git, never hand-edited):
#   CLAUDE.md                    — Claude-specific header + AGENTS.md appended
#   .claude/skills/*/SKILL.md   — Copy from .agents/skills/ (Claude Code native)
#   gemini-scribe/Skills/*/SKILL.md — Copy for the Obsidian Gemini Scribe plugin
#
# Run this before releasing a new COG version.
#
# Usage:
#   ./cog-sync.sh               Sync all generated files
#   ./cog-sync.sh --dry-run     Show what would change (no writes)
#   ./cog-sync.sh --check       Parity check only (no writes)
#   ./cog-sync.sh --help        Show help
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${CYAN}i${RESET}  $*"; }
ok()    { echo -e "${GREEN}+${RESET}  $*"; }
warn()  { echo -e "${YELLOW}!${RESET}  $*"; }
err()   { echo -e "${RED}x${RESET}  $*" >&2; }

# ── Paths ───────────────────────────────────────────────────────────
SOURCE_DIR=".agents/skills"
CLAUDE_DIR=".claude/skills"

# Gemini Scribe (Obsidian plugin) discovers skills only under its state folder,
# and its discovery walks Obsidian's file index — which excludes dot-folders.
# So .agents/skills is unreachable and this mirror is required.
SCRIBE_DIR="gemini-scribe/Skills"

# Output styles replace the agent's response voice. Claude Code discovers them
# under .claude/output-styles/; the source lives with the rest of the framework.
STYLE_SOURCE_DIR=".agents/output-styles"
CLAUDE_STYLE_DIR=".claude/output-styles"

# Skills maintained directly in the tool dirs (not generated from SOURCE_DIR).
# cog-sync must never treat these as orphans and delete them.
EXTERNAL_SKILLS=("playwriter" "czech-ai-news")

is_external_skill() {
  local check="$1"
  for ext in "${EXTERNAL_SKILLS[@]}"; do
    [[ "$ext" == "$check" ]] && return 0
  done
  return 1
}

# ── Marker for hybrid context files ────────────────────────────────
AUTOGEN_MARKER="<!-- AUTO-GENERATED: Everything below is synced from AGENTS.md by cog-sync.sh — do not edit manually -->"

# ── YAML frontmatter helpers ────────────────────────────────────────

# Extract a top-level frontmatter field value
# Usage: get_field "name" "path/to/SKILL.md"
get_field() {
  local field="$1" file="$2"
  tr -d '\r' < "$file" | sed -n '1,/^---$/!b; /^---$/,/^---$/{ /^'"$field"':/{ s/^'"$field"':[[:space:]]*//; s/^"//; s/"$//; p; } }' 2>/dev/null | head -1
}

# ── Usage ───────────────────────────────────────────────────────────
usage() {
  cat <<'EOF'
COG Skill Sync — Generate tool-specific files from source of truth

Source of truth:
  AGENTS.md                   Framework docs and skill descriptions
  .agents/skills/*/SKILL.md   Full skill playbooks (agentskills.io standard)
  .agents/output-styles/*.md  Response-voice styles

Generated files (committed to git):
  CLAUDE.md                   Claude-specific header + AGENTS.md content
  .claude/skills/*/SKILL.md   Copies for Claude Code native discovery
  .claude/output-styles/*.md  Copies for Claude Code style discovery
  gemini-scribe/Skills/       Copies for the Obsidian Gemini Scribe plugin

Usage:
  ./cog-sync.sh               Sync all generated files
  ./cog-sync.sh --dry-run     Preview changes without writing
  ./cog-sync.sh --check       Parity check only
  ./cog-sync.sh --help        This message

Run before releasing a new COG version.
EOF
}

# ── Parity check ────────────────────────────────────────────────────
parity_check() {
  local issues=0

  echo -e "${BOLD}Parity check${RESET}"
  echo ""

  # 1. Check generated files exist for each source skill
  for skill_dir in "${SOURCE_DIR}"/*/; do
    [[ -d "$skill_dir" ]] || continue
    local skill_file="${skill_dir}SKILL.md"
    [[ -f "$skill_file" ]] || continue

    local name
    name=$(get_field "name" "$skill_file")
    [[ -z "$name" ]] && continue

    [[ ! -f "${CLAUDE_DIR}/${name}/SKILL.md" ]] && warn "Missing: ${CLAUDE_DIR}/${name}/SKILL.md" && issues=$((issues + 1))
    [[ ! -f "${SCRIBE_DIR}/${name}/SKILL.md" ]] && warn "Missing: ${SCRIBE_DIR}/${name}/SKILL.md" && issues=$((issues + 1))
  done

  # 2. Check generated copies exist for each output style
  for style_file in "${STYLE_SOURCE_DIR}"/*.md; do
    [[ -f "$style_file" ]] || continue
    local style_name
    style_name=$(basename "$style_file")
    [[ "$style_name" == "README.md" ]] && continue
    [[ ! -f "${CLAUDE_STYLE_DIR}/${style_name}" ]] && warn "Missing: ${CLAUDE_STYLE_DIR}/${style_name}" && issues=$((issues + 1))
  done

  # 3. Check context files contain AGENTS.md content
  for ctx_file in CLAUDE.md; do
    if [[ -f "$ctx_file" ]]; then
      # Verify AGENTS.md content is present (either as pure copy or after marker)
      local first_agents_line
      first_agents_line=$(head -1 AGENTS.md)
      if ! grep -qF "$first_agents_line" "$ctx_file" 2>/dev/null; then
        warn "${ctx_file} out of sync with AGENTS.md"
        issues=$((issues + 1))
      fi
    else
      warn "Missing: ${ctx_file}"
      issues=$((issues + 1))
    fi
  done

  echo ""
  if [[ $issues -eq 0 ]]; then
    ok "All files in sync"
  else
    warn "${issues} issue(s) found — run ${BOLD}./cog-sync.sh${RESET} to fix"
  fi

  return $issues
}

# ── Sync one skill ──────────────────────────────────────────────────
sync_skill() {
  local skill_file="$1" dry_run="$2"
  local name

  name=$(get_field "name" "$skill_file")
  if [[ -z "$name" ]]; then
    warn "Skipping ${skill_file} — no 'name' in frontmatter"
    return 1
  fi

  info "Syncing: ${BOLD}${name}${RESET}"

  # Gemini Scribe validates skill names and silently drops the ones it rejects,
  # so a bad name would work in Claude Code and vanish in Obsidian.
  if [[ ! "$name" =~ ^[a-z]([a-z0-9]|-[a-z0-9])*$ ]]; then
    warn "  ${name} — Gemini Scribe will reject this name (lowercase, digits, single hyphens, must start with a letter)"
  fi

  # ── Copy as-is into each tool directory ────────────────────────
  local skill_base
  skill_base=$(dirname "$skill_file")

  for tool_dir in "$CLAUDE_DIR" "$SCRIBE_DIR"; do
    local target="${tool_dir}/${name}/SKILL.md"

    if $dry_run; then
      echo "    ${target}"
      continue
    fi

    mkdir -p "${tool_dir}/${name}"
    cp "$skill_file" "$target"

    # Also copy scripts/, references/, assets/ if they exist
    for subdir in scripts references assets; do
      if [[ -d "${skill_base}/${subdir}" ]]; then
        cp -r "${skill_base}/${subdir}" "${tool_dir}/${name}/"
      fi
    done
  done

  return 0
}

# ── Sync output styles ────────────────────────────────────────────
# Copies every style in STYLE_SOURCE_DIR into the Claude Code style dir.
# README.md documents the styles for humans and is not itself a style.
sync_output_styles() {
  local dry_run="$1"
  local synced=0

  for style_file in "${STYLE_SOURCE_DIR}"/*.md; do
    [[ -f "$style_file" ]] || continue

    local style_name
    style_name=$(basename "$style_file")
    [[ "$style_name" == "README.md" ]] && continue

    local target="${CLAUDE_STYLE_DIR}/${style_name}"

    if $dry_run; then
      echo "    ${target}"
    else
      mkdir -p "$CLAUDE_STYLE_DIR"
      cp "$style_file" "$target"
      ok "  ${target}"
    fi
    synced=$((synced + 1))
  done

  [[ $synced -eq 0 ]] && info "  No output styles found in ${STYLE_SOURCE_DIR}/"

  return 0
}

# ── Sync context file ─────────────────────────────────────────────
# Copies AGENTS.md to the target file. If the target has content above
# the auto-gen marker, that header is preserved; otherwise the file
# becomes a pure copy of AGENTS.md.
sync_context_file() {
  local target="$1" dry_run="$2"

  if $dry_run; then
    echo "    ${target} (copy of AGENTS.md)"
    return 0
  fi

  if [[ -f "$target" ]] && grep -qF "$AUTOGEN_MARKER" "$target" 2>/dev/null; then
    # Check if there's meaningful content above the marker
    local header
    header=$(awk -v marker="$AUTOGEN_MARKER" 'index($0, marker){exit} {print}' "$target" | grep -v '^[[:space:]]*$' || true)
    if [[ -n "$header" ]]; then
      # Preserve header above marker, replace everything below
      awk -v marker="$AUTOGEN_MARKER" '
        { print }
        index($0, marker) { found=1; exit }
        END { if (!found) print marker }
      ' "$target" > "${target}.tmp"
      echo "" >> "${target}.tmp"
      cat AGENTS.md >> "${target}.tmp"
      mv "${target}.tmp" "$target"
      ok "  ${target} (header + AGENTS.md)"
    else
      # No meaningful header — pure copy
      cp AGENTS.md "$target"
      ok "  ${target} (copy)"
    fi
  else
    # No marker or file doesn't exist — pure copy
    cp AGENTS.md "$target"
    ok "  ${target} (copy)"
  fi
}

# ── Clean up orphaned generated files ──────────────────────────────
cleanup_orphans() {
  local dry_run="$1"
  local removed=0

  info "Checking for orphaned generated files..."

  # Build set of expected skill names from source
  local -a source_names=()
  for d in "${SOURCE_DIR}"/*/; do
    [[ -d "$d" ]] || continue
    local skill_file="${d}SKILL.md"
    [[ -f "$skill_file" ]] || continue
    local sname
    sname=$(get_field "name" "$skill_file")
    [[ -n "$sname" ]] && source_names+=("$sname")
  done

  # Helper: check if name is in source_names
  is_source_skill() {
    local check="$1"
    for sn in "${source_names[@]}"; do
      [[ "$sn" == "$check" ]] && return 0
    done
    return 1
  }

  # Generated skill copies
  for tool_dir in "$CLAUDE_DIR" "$SCRIBE_DIR"; do
    for d in "${tool_dir}"/*/; do
      [[ -d "$d" ]] || continue
      local skill_name
      skill_name=$(basename "$d")
      is_external_skill "$skill_name" && continue
      if ! is_source_skill "$skill_name"; then
        warn "Orphaned: ${d}"
        if ! $dry_run; then rm -rf "$d"; ok "  Removed: ${d}"; fi
        removed=$((removed + 1))
      fi
    done
  done

  # Generated output-style copies
  for f in "${CLAUDE_STYLE_DIR}"/*.md; do
    [[ -f "$f" ]] || continue
    local style_name
    style_name=$(basename "$f")
    if [[ ! -f "${STYLE_SOURCE_DIR}/${style_name}" ]]; then
      warn "Orphaned: ${f}"
      if ! $dry_run; then rm -f "$f"; ok "  Removed: ${f}"; fi
      removed=$((removed + 1))
    fi
  done

  if [[ $removed -eq 0 ]]; then
    ok "No orphaned files found"
  else
    if $dry_run; then
      warn "Found ${removed} orphaned item(s) — will be removed on sync"
    else
      ok "Removed ${removed} orphaned item(s)"
    fi
  fi
}

# ── Main ────────────────────────────────────────────────────────────
main() {
  local mode="sync"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) mode="dry-run"; shift ;;
      --check)   mode="check";   shift ;;
      --help|-h) usage; exit 0 ;;
      *) err "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  echo ""
  echo -e "${BOLD}COG Skill Sync${RESET}"
  echo -e "──────────────"
  echo ""

  # Validate source of truth exists
  if [[ ! -f "AGENTS.md" ]]; then
    err "AGENTS.md not found. Run from the COG root directory."
    exit 1
  fi

  if [[ ! -d "$SOURCE_DIR" ]]; then
    err "Source directory ${SOURCE_DIR}/ not found."
    err "Skills must live in .agents/skills/*/SKILL.md (agentskills.io standard)."
    exit 1
  fi

  # Count skills
  local skill_count=0
  for d in "${SOURCE_DIR}"/*/; do
    [[ -f "${d}SKILL.md" ]] && skill_count=$((skill_count + 1))
  done
  info "Found ${BOLD}${skill_count}${RESET} skills in ${SOURCE_DIR}/"
  echo ""

  # ── Check mode ─────────────────────────────────────────────────
  if [[ "$mode" == "check" ]]; then
    parity_check
    exit $?
  fi

  local dry_run=false
  [[ "$mode" == "dry-run" ]] && dry_run=true

  $dry_run && info "Dry run — no files will be written" && echo ""

  # ── Sync context files (hybrid: header + AGENTS.md) ────────────
  info "Context files:"
  sync_context_file "CLAUDE.md" "$dry_run"
  echo ""

  # ── Sync each skill ───────────────────────────────────────────
  local synced=0 errors=0
  info "Skills:"
  echo ""

  for skill_dir in "${SOURCE_DIR}"/*/; do
    [[ -d "$skill_dir" ]] || continue
    local skill_file="${skill_dir}SKILL.md"
    [[ -f "$skill_file" ]] || continue

    if sync_skill "$skill_file" "$dry_run"; then
      synced=$((synced + 1))
    else
      errors=$((errors + 1))
    fi
  done

  # ── Sync output styles ────────────────────────────────────────
  echo ""
  info "Output styles:"
  sync_output_styles "$dry_run"

  # ── Clean up orphans ──────────────────────────────────────────
  echo ""
  cleanup_orphans "$dry_run"

  # ── Summary ────────────────────────────────────────────────────
  echo ""
  echo -e "${BOLD}Summary${RESET}"
  ok "Synced ${synced} skills to Claude Code and Gemini Scribe"
  ok "Synced output styles to Claude Code"
  ok "Synced CLAUDE.md from AGENTS.md"
  [[ $errors -gt 0 ]] && warn "${errors} skill(s) skipped due to errors"

  if ! $dry_run; then
    echo ""

    # Run parity check
    echo ""
    parity_check || true

    echo ""
    info "Review with ${BOLD}git diff${RESET}, then commit when ready."
  fi
}

main "$@"
