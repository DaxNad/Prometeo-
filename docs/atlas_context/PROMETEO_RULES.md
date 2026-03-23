# REGOLE OPERATIVE PROMETEO

1. non sovrascrivere file esistenti senza confronto diff
2. ogni script deve essere eseguibile da terminale mac
3. smf_update.py deve rimanere compatibile con ~/Documents/local_smf
4. PostgreSQL deve restare database principale
5. ogni modifica deve mantenere compatibilità Railway
6. ogni configurazione Codex deve essere locale al progetto: .codex/config.toml

Config standard Codex:
model = "gpt-5"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

7. pipeline standard:
- ChatGPT → progettazione logica
- Codex → generazione codice
- Terminale → esecuzione
- Browser → verifica UI
- PostgreSQL → persistenza
- Git → versionamento
- Railway → deploy

8. obiettivo medio termine:
PWA gestionale PROMETEO

9. obiettivo lungo termine:
AI orchestration completa produzione

10. regola di stabilità:
integrazione incrementale
mai refactor distruttivo globale
