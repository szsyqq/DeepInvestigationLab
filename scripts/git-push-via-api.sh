#!/bin/bash
# Git Push via GitHub API (fallback when git push fails with proxy 502)
# Usage: bash scripts/git-push-via-api.sh <file_path> <commit_message>
# Example: bash scripts/git-push-via-api.sh portal/reports/fund-gray/index.html "fix: update report"

set -euo pipefail

FILE_PATH="${1:?Usage: $0 <file_path> <commit_message>}"
COMMIT_MSG="${2:?Usage: $0 <file_path> <commit_message>}"
REPO="szsyqq/DeepInvestigationLab"

# Verify file exists
[ ! -f "$FILE_PATH" ] && echo "❌ File not found: $FILE_PATH" && exit 1

echo "🔍 Fetching latest commit from main..."
LATEST=$(gh api repos/$REPO/git/refs/heads/main --jq '.object.sha')
echo "   Latest commit: $LATEST"

TREE=$(gh api repos/$REPO/git/commits/$LATEST --jq '.tree.sha')
echo "   Current tree: $TREE"

echo "📦 Creating blob..."
BASE64=$(base64 -i "$FILE_PATH")
BLOB=$(echo "{\"content\":\"$BASE64\",\"encoding\":\"base64\"}" | \
  gh api repos/$REPO/git/blobs --input - --jq '.sha')
echo "   Blob SHA: $BLOB"

echo "🌳 Creating tree..."
NEW_TREE=$(echo "{\"base_tree\":\"$TREE\",\"tree\":[{\"path\":\"$FILE_PATH\",\"mode\":\"100644\",\"type\":\"blob\",\"sha\":\"$BLOB\"}]}" | \
  gh api repos/$REPO/git/trees --input - --jq '.sha')
echo "   New tree: $NEW_TREE"

echo "✍️  Creating commit..."
NEW_COMMIT=$(echo "{\"message\":\"$COMMIT_MSG\",\"tree\":\"$NEW_TREE\",\"parents\":[\"$LATEST\"]}" | \
  gh api repos/$REPO/git/commits --input - --jq '.sha')
echo "   New commit: $NEW_COMMIT"

echo "🚀 Updating main branch..."
echo "{\"sha\":\"$NEW_COMMIT\",\"force\":true}" | \
  gh api repos/$REPO/git/refs/heads/main -X PATCH --input - > /dev/null
echo "✅ Done! GitHub Actions will deploy automatically."
echo ""
echo "⚠️  Note: Local git history will diverge. Run this to sync:"
echo "   git fetch --all && git reset --hard origin/main"
