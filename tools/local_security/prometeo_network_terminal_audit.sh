#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SAFE_CODEX_DIR="${PROMETEO_SAFE_CODEX_DIR:-$HOME/PROMETEO_SAFE_CODEX}"
REPORT_DIR="$ROOT/data/local_reports/network_terminal_audit"
QUARANTINE_DIR="$REPORT_DIR/quarantine_launchagents"
TS="$(date '+%Y%m%d_%H%M%S')"
REPORT="$REPORT_DIR/audit_$TS.md"

mkdir -p "$REPORT_DIR" "$QUARANTINE_DIR"

redact() {
  sed -E \
    -e 's/(g[h]p_)[A-Za-z0-9_]+/\1***REDACTED***/g' \
    -e 's/(github_[p]at_)[A-Za-z0-9_]+/\1***REDACTED***/g' \
    -e 's/(s[k]-[A-Za-z0-9_-]+)/secret-key-REDACTED/g' \
    -e 's#(postgresql:/{2})[^[:space:]]+#\1***REDACTED***#g' \
    -e 's#(DATABASE_URL=)[^[:space:]]+#\1***REDACTED***#g' \
    -e 's#(PROMETEO_API_KEY=)[^[:space:]]+#\1***REDACTED***#g' \
    -e 's#(OPENAI_API_KEY=)[^[:space:]]+#\1***REDACTED***#g' \
    -e 's#(ANTHROPIC_API_KEY=)[^[:space:]]+#\1***REDACTED***#g'
}

write() {
  printf '%s\n' "$*" >> "$REPORT"
}

section() {
  {
    printf '\n## %s\n\n' "$1"
  } >> "$REPORT"
}

run_cmd() {
  local title="$1"
  shift
  section "$title"
  {
    printf '```text\n'
    "$@" 2>&1 | redact || true
    printf '```\n'
  } >> "$REPORT"
}

flag() {
  write "- $1"
}

cat > "$REPORT" << EOF
# PROMETEO — Terminale / Rete / Daemon Audit

Data: $(date)
Host: $(hostname)
Utente: $(whoami)
Root atteso: $ROOT

EOF

section "Semaforo sintetico"
write "Valutazione iniziale generata da audit locale. Leggere la sezione finale \`Esito guard rail\`."

run_cmd "Sistema" sw_vers
run_cmd "Utente e shell" sh -c 'id && printf "SHELL=%s\nHOME=%s\nPWD=%s\n" "$SHELL" "$HOME" "$PWD"'
run_cmd "Repo status" sh -c 'cd "$ROOT" && git status -sb && git branch --show-current && git log --oneline -5'
run_cmd "Remote Git redatto" sh -c 'cd "$ROOT" && git remote -v'
run_cmd "Processi PROMETEO / AI / dev" sh -c 'ps axww -o pid,ppid,user,stat,command | grep -Ei "PROMETEO|uvicorn|fastapi|ollama|codex|mimo|railway|vercel|node|vite|postgres" | grep -v grep'
run_cmd "Porte TCP in ascolto" sh -c 'lsof -nP -iTCP -sTCP:LISTEN'
run_cmd "Porte critiche note" sh -c '
for p in 8000 5173 11434 5432 22 80 443; do
  echo "--- PORT $p ---"
  lsof -nP -iTCP:$p -sTCP:LISTEN || true
done
'
run_cmd "Launchctl rilevante" sh -c 'launchctl list | grep -Ei "ollama|codex|prometeo|uvicorn|python|node|railway|vercel" || true'
run_cmd "LaunchAgents/Daemons rilevanti" sh -c '
find "$HOME/Library/LaunchAgents" /Library/LaunchAgents /Library/LaunchDaemons \
  -maxdepth 1 -type f \( \
    -iname "*ollama*" -o \
    -iname "*codex*" -o \
    -iname "*prometeo*" -o \
    -iname "*uvicorn*" -o \
    -iname "*python*" -o \
    -iname "*node*" \
  \) 2>/dev/null | sort
'
run_cmd "Contenuto plist sospetti redatto" sh -c '
for f in $(find "$HOME/Library/LaunchAgents" /Library/LaunchAgents /Library/LaunchDaemons \
  -maxdepth 1 -type f \( -iname "*codex*" -o -iname "*prometeo*" -o -iname "*uvicorn*" -o -iname "*python*" -o -iname "*node*" \) 2>/dev/null | sort); do
  echo "===== $f ====="
  plutil -p "$f" 2>/dev/null || cat "$f"
done
'
run_cmd "Profili shell — solo righe rilevanti redatte" sh -c '
for f in "$HOME/.zshrc" "$HOME/.zprofile" "$HOME/.profile" "$HOME/.bash_profile" "$HOME/.bashrc"; do
  [ -f "$f" ] || continue
  echo "===== $f ====="
  grep -nEi "PROMETEO|codex|ollama|DATABASE_URL|API_KEY|TOKEN|SECRET|g[h]p_|github_[p]at_|s[k]-" "$f" || true
done
'
run_cmd "File iCloud check" sh -c '
case "$ROOT" in
  *"Mobile Documents"*|*"iCloud"*) echo "CRITICAL: PROMETEO sembra dentro iCloud" ;;
  *) echo "OK: PROMETEO non risulta in path iCloud" ;;
esac
'

section "Fix idempotenti applicati"

FIXES=0
WARNINGS=0
CRITICAL=0

# 1. Vietato Codex daemon/LaunchAgent utente.
# Disabilita solo plist utente chiaramente Codex. Non tocca /Library senza sudo.
while IFS= read -r plist; do
  [ -n "$plist" ] || continue
  base="$(basename "$plist")"
  backup="$QUARANTINE_DIR/${base}.${TS}.disabled"
  echo "Trovato LaunchAgent Codex utente: $plist" >> "$REPORT"
  echo "Azione: bootout best-effort + spostamento in quarantena: $backup" >> "$REPORT"
  launchctl bootout "gui/$(id -u)" "$plist" >> "$REPORT" 2>&1 || true
  mv "$plist" "$backup"
  FIXES=$((FIXES + 1))
done < <(find "$HOME/Library/LaunchAgents" -maxdepth 1 -type f -iname "*codex*" 2>/dev/null | sort)

# 2. Segnala, ma non tocca, daemon di sistema Codex.
SYSTEM_CODEX="$(find /Library/LaunchAgents /Library/LaunchDaemons -maxdepth 1 -type f -iname "*codex*" 2>/dev/null | sort || true)"
if [ -n "$SYSTEM_CODEX" ]; then
  WARNINGS=$((WARNINGS + 1))
  {
    echo ""
    echo "WARNING: trovati plist Codex in /Library. Non modificati perché richiedono valutazione/sudo:"
    echo "$SYSTEM_CODEX"
  } >> "$REPORT"
fi

# 3. Codex in processo vivo: distingue safe Codex da Codex fuori policy.
CODEX_PROC="$(ps axww -o pid,command | grep -Ei "codex|ollama launch codex|codex-app" | grep -v grep || true)"
if [ -n "$CODEX_PROC" ]; then
  SAFE_CODEX_PATTERN="--profile prometeo_safe_codex.*--sandbox read-only.*--cd ${SAFE_CODEX_DIR}|--cd ${SAFE_CODEX_DIR}.*--profile prometeo_safe_codex.*--sandbox read-only"
  UNSAFE_CODEX="$(printf '%s\n' "$CODEX_PROC" | grep -Ev -- "$SAFE_CODEX_PATTERN" || true)"
  SAFE_CODEX="$(printf '%s\n' "$CODEX_PROC" | grep -E -- "$SAFE_CODEX_PATTERN" || true)"

  if [ -n "$SAFE_CODEX" ]; then
    {
      echo ""
      echo "INFO: processi Codex sicuri rilevati:"
      echo "$SAFE_CODEX" | redact
    } >> "$REPORT"
  fi

  if [ -n "$UNSAFE_CODEX" ]; then
    WARNINGS=$((WARNINGS + 1))
    {
      echo ""
      echo "WARNING: processi Codex fuori policy rilevati. Non terminati automaticamente:"
      echo "$UNSAFE_CODEX" | redact
    } >> "$REPORT"
  fi
fi

# 4. Ollama ammesso solo locale.
if lsof -nP -iTCP:11434 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
  OLLAMA_BIND="$(lsof -nP -iTCP:11434 -sTCP:LISTEN 2>/dev/null | awk 'NR>1 {print $9}' | sort -u)"
  {
    echo ""
    echo "Ollama porta 11434:"
    echo "$OLLAMA_BIND"
  } >> "$REPORT"

  if echo "$OLLAMA_BIND" | grep -Evq '127\.0\.0\.1:11434|localhost:11434|\[::1\]:11434'; then
    WARNINGS=$((WARNINGS + 1))
    echo "WARNING: verificare binding Ollama. Preferibile localhost only." >> "$REPORT"
  fi
else
  echo "INFO: Ollama non risulta in ascolto su 11434 al momento dell'audit." >> "$REPORT"
fi

# 5. Porte pubbliche 80/443: segnalazione.
if lsof -nP -iTCP:80 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN || lsof -nP -iTCP:443 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
  WARNINGS=$((WARNINGS + 1))
  echo "WARNING: porte 80/443 in ascolto. Verificare che PROMETEO non sia esposto pubblicamente." >> "$REPORT"
fi

# 6. Branch main: segnala come blocco operativo.
CURRENT_BRANCH="$(cd "$ROOT" && git branch --show-current || true)"
if [ "$CURRENT_BRANCH" = "main" ]; then
  WARNINGS=$((WARNINGS + 1))
  echo "WARNING: repo su main. Vietato commit/push diretto. Creare branch dedicato prima di modifiche." >> "$REPORT"
fi

section "Esito guard rail"

if [ "$FIXES" -gt 0 ]; then
  flag "GIALLO: applicati $FIXES fix idempotenti su LaunchAgent Codex utente."
fi

if [ "$WARNINGS" -gt 0 ]; then
  flag "GIALLO: rilevati $WARNINGS punti da verificare."
else
  flag "VERDE: nessun daemon/processo/punto rete critico rilevato dalle regole locali."
fi

if [ "$CRITICAL" -gt 0 ]; then
  flag "ROSSO: rilevati $CRITICAL problemi critici."
fi

flag "Report: $REPORT"
flag "Quarantena eventuale: $QUARANTINE_DIR"

printf '\n=== PROMETEO AUDIT COMPLETATO ===\n'
printf 'Report: %s\n' "$REPORT"
printf 'Fix applicati: %s\n' "$FIXES"
printf 'Warning: %s\n' "$WARNINGS"
printf '\nApri report con:\ncat "%s"\n' "$REPORT"
