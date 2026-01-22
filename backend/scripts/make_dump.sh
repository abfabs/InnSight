#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${1:-innsight_db}"
MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"
OUT_DIR="${OUT_DIR:-db_dump}"

echo "📦 Creating Mongo dump..."
echo "   DB:  $DB_NAME"
echo "   URI: $MONGO_URI"
echo "   OUT: $OUT_DIR/$DB_NAME"

mkdir -p "$OUT_DIR"

# Remove old dump so deleted collections don’t linger
rm -rf "$OUT_DIR/$DB_NAME"

mongodump --uri="$MONGO_URI" --db "$DB_NAME" --out "$OUT_DIR"

echo "✅ Dump created at: $OUT_DIR/$DB_NAME"
du -sh "$OUT_DIR/$DB_NAME" || true

echo
echo "Next:"
echo "  git add $OUT_DIR/$DB_NAME"
echo "  git commit -m \"Update Mongo dump\""
echo "  git push"
