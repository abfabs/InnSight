#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${1:-innsight_db}"
MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"
DUMP_PATH="db_dump/$DB_NAME"

echo "🔄 Updating local DB from repo dump..."
echo "   DB:   $DB_NAME"
echo "   URI:  $MONGO_URI"
echo "   DUMP: $DUMP_PATH"

# Ensure we are in the repo root (script can be run from anywhere)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Pull latest code + LFS files
git pull
git lfs pull

# Sanity checks
if [ ! -d "$DUMP_PATH" ]; then
  echo "❌ Dump folder not found: $DUMP_PATH"
  echo "Make sure you pulled LFS files: git lfs pull"
  exit 1
fi

if ! command -v mongorestore >/dev/null; then
  echo "❌ mongorestore not found. Install MongoDB Database Tools."
  echo "   Ubuntu/Debian: sudo apt install -y mongodb-database-tools"
  exit 1
fi

# Restore (drop existing DB contents first)
mongorestore --uri="$MONGO_URI" --db "$DB_NAME" --drop "$DUMP_PATH"

echo "✅ Restore complete."

# Quick verification
echo "📋 Collections:"
mongosh --quiet --eval "use $DB_NAME; show collections" || true
