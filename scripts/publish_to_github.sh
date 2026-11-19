#!/usr/bin/env bash
# Publish SDET-TechAssessment to mummineninithesh-del (run off Swiggy VPN / on mobile hotspot).
set -euo pipefail

REPO="mummineninithesh-del/SDET-TechAssessment"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "→ Active GitHub account:"
gh auth switch -h github.com -u mummineninithesh-del
gh auth status -h github.com

if git remote get-url origin &>/dev/null; then
  git remote set-url origin "https://github.com/${REPO}.git"
else
  git remote add origin "https://github.com/${REPO}.git"
fi

if ! gh repo view "$REPO" &>/dev/null; then
  echo "→ Swiggy/corp network often blocks 'gh repo create' (api.github.com)."
  echo "→ Create the public repo in your browser (no README), then re-run this script:"
  echo "   https://github.com/new?name=SDET-TechAssessment&visibility=public"
  exit 1
fi

git remote remove origin 2>/dev/null || true
if ! git remote get-url origin &>/dev/null; then
  git remote add origin "git@github.com:${REPO}.git"
fi

echo "→ Pushing via SSH (usually allowed when API is blocked)..."
git push -u origin main

echo "Done: https://github.com/${REPO}"