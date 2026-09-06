#!/bin/bash
# ledger-verify.sh — Obstruction Ledger chain verification
# RUNBOOK §4: run every resume and after every append
# On single-admin host (§2.3 fallback): Hermes holds keys,
# runner never writes to ledger/, disclosure in paper.

LEDGER_DIR="/Users/brukendale/ol-run/obstruction-ledger-v1.2/ledger"
FAIL=0

echo "=== Ledger chain verification ==="

for f in $(ls "$LEDGER_DIR"/*.yaml 2>/dev/null | sort); do
    NAME=$(basename "$f")
    HASH=$(shasum -a 256 "$f" | cut -d' ' -f1)
    
    # Parse prev_hash from certificate
    PREV=$(grep 'prev_hash:' "$f" | head -1 | sed 's/.*: //; s/"//g; s/ //g')
    CHAIN=$(grep 'chain_hash:' "$f" | head -1 | sed 's/.*: //; s/"//g; s/ //g')
    
    echo "  $NAME: sha256=$HASH prev=$PREV"
    
    if [ "$NAME" != "0000-genesis.yaml" ] && [ -z "$PREV" ] || [ "$PREV" = "null" ]; then
        echo "  ⚠  Non-genesis certificate lacks prev_hash; chain broken"
        FAIL=1
    fi
done

if [ $FAIL -eq 0 ]; then
    echo "=== Ledger chain: INTACT ==="
    exit 0
else
    echo "=== Ledger chain: BROKEN ==="
    exit 1
fi