# smf-webhook (ready)

Webhook per Vercel con verifica `X-Hub-Signature-256` su **raw body** (HMAC SHA-256).
Configurazione **minimal** senza `builds` legacy o `now.*`.

## Setup rapido
1. **Vercel → Project → Settings → Environment**: aggiungi `WEBHOOK_SECRET` (Production/Preview/Development).
2. **GitHub → Repo → Settings → Webhooks**:
   - Payload URL: `https://<nome-progetto>.vercel.app/api/webhook`
   - Content type: `application/json`
   - **Secret**: lo stesso valore di `WEBHOOK_SECRET`
3. **Deploy**: connetti il repo a Vercel (Project → Import) o push se già connesso.
4. **Test**: GitHub → Webhooks → Recent Deliveries → **Redeliver** → atteso `200 OK`.

## Test locale della firma
Genera una firma coerente con:
```bash
node tests/sign.js '{"zen":"Keep it logically awesome"}' your_secret_here
```
E prova la route:
```bash
curl -X POST "http://localhost:3000/api/webhook"     -H "Content-Type: application/json"     -H "X-Hub-Signature-256: sha256=<firma_generata>"     --data '{"zen":"Keep it logically awesome"}'
```

> Per eseguire in locale: `npm i` (opzionale) e `npx vercel dev`.
