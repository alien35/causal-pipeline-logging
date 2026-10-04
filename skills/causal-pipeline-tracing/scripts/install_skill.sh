#!/usr/bin/env bash
# install_skill.sh - Installs causal-pipeline-tracing skill into a target repository or global agent config

set -euo pipefail

TARGET_DIR="."
INSTALL_CLAUDE=false
INSTALL_CODEX=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude)
      INSTALL_CLAUDE=true
      shift
      ;;
    --codex)
      INSTALL_CODEX=true
      shift
      ;;
    --all)
      INSTALL_CLAUDE=true
      INSTALL_CODEX=true
      shift
      ;;
    -h|--help)
      echo "Usage: install_skill.sh [options] [TARGET_DIR]"
      echo ""
      echo "Options:"
      echo "  --claude      Configure for Claude Code (adds/updates CLAUDE.md)"
      echo "  --codex       Configure for OpenAI Codex / Copilot (adds/updates AGENTS.md)"
      echo "  --all         Configure for Antigravity, Claude Code, and Codex"
      echo "  -h, --help    Show this help message"
      exit 0
      ;;
    *)
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${SKILL_SOURCE}/../../.." && pwd)"

echo "🚀 Installing 'causal-pipeline-tracing' skill..."
echo "📂 Source: ${SKILL_SOURCE}"
echo "🎯 Target: ${TARGET_DIR}"

DEST_DIR="${TARGET_DIR}/.agents/skills/causal-pipeline-tracing"
mkdir -p "${DEST_DIR}"

cp -R "${SKILL_SOURCE}/SKILL.md" "${DEST_DIR}/"
cp -R "${SKILL_SOURCE}/references" "${DEST_DIR}/"
cp -R "${SKILL_SOURCE}/examples" "${DEST_DIR}/"
cp -R "${SKILL_SOURCE}/scripts" "${DEST_DIR}/"

echo "✅ Skill successfully installed at ${DEST_DIR}"

# Claude Code integration
if [ "${INSTALL_CLAUDE}" = true ]; then
  CLAUDE_FILE="${TARGET_DIR}/CLAUDE.md"
  CLAUDE_SRC="${REPO_ROOT}/integrations/claude-code/CLAUDE.md"
  if [ -f "${CLAUDE_SRC}" ]; then
    echo "🤖 Adding Claude Code instructions to ${CLAUDE_FILE}..."
    if [ -f "${CLAUDE_FILE}" ]; then
      echo -e "\n\n" >> "${CLAUDE_FILE}"
      cat "${CLAUDE_SRC}" >> "${CLAUDE_FILE}"
    else
      cp "${CLAUDE_SRC}" "${CLAUDE_FILE}"
    fi
    echo "✅ Claude Code configured (${CLAUDE_FILE})."
  fi
fi

# OpenAI Codex integration
if [ "${INSTALL_CODEX}" = true ]; then
  AGENTS_FILE="${TARGET_DIR}/AGENTS.md"
  CODEX_SRC="${REPO_ROOT}/integrations/codex/CODEX.md"
  if [ -f "${CODEX_SRC}" ]; then
    echo "⚡ Adding Codex / Copilot instructions to ${AGENTS_FILE}..."
    if [ -f "${AGENTS_FILE}" ]; then
      echo -e "\n\n" >> "${AGENTS_FILE}"
      cat "${CODEX_SRC}" >> "${AGENTS_FILE}"
    else
      cp "${CODEX_SRC}" "${AGENTS_FILE}"
    fi
    echo "✅ Codex configured (${AGENTS_FILE})."
  fi
fi

echo ""
echo "💡 Usage:"
echo "• Antigravity: Ask your assistant: 'Use causal-pipeline-tracing skill to improve queue logging.'"
echo "• Claude Code: Run: claude 'Apply causal-pipeline-tracing to our async queues per CLAUDE.md'"
echo "• OpenAI Codex: Prompt Codex with the instructions in AGENTS.md / CODEX.md."
