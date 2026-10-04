#!/usr/bin/env bash
# install_skill.sh - Installs causal-pipeline-tracing skill into a target repository or global agent config

set -euo pipefail

TARGET_DIR="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$(cd "${SCRIPT_DIR}/.." && pwd)"

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
echo ""
echo "💡 Usage:"
echo "Prompt your AI assistant:"
echo "  'Use the causal-pipeline-tracing skill to audit our asynchronous event and outbox pipelines and improve our logging.'"
