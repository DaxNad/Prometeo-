# LLM GOVERNANCE PROMETEO

## Scopo

Questo documento è prima lettura obbligatoria per ogni lavoro PROMETEO che coinvolge AI, TL Chat, ATLAS Engine, retrieval, eval o agenti.

## Architettura da preservare

Order
→ Route
→ Station
→ ProductionEvent

PROMETEO Core = deterministico  
ATLAS Engine = reasoning controllato  
LLM = supporto contestuale  
Retrieval = recupero fonti autorizzate  
Eval = verifica qualità  
TL / Human-in-the-loop = autorità finale

## Regola fondamentale

Fine-tuning = ultima opzione.

Prima usare:

1. retrieval
2. regole deterministiche
3. guardrail
4. eval
5. audit log
6. conferma umana

## Cosa NON affidare al modello

- verità produttiva definitiva
- decisioni automatiche
- modifica dati reali senza conferma
- planner libero
- agenti non controllati
- fonti non autorizzate
- contesto enorme non selezionato

## Pattern corretto

Domanda operativa
→ retrieval fonti autorizzate
→ output JSON controllato
→ validazione schema
→ eval
→ risposta breve
→ audit log
→ eventuale conferma umana

## Pattern vietato

LLM libero
→ risposta plausibile
→ fiducia automatica
→ modifica sistema

## PROMETEO_RAG_EVAL_001

Input:
- domanda operativa

Retrieval:
- fonti locali autorizzate

Output:
- risposta controllata
- fonte
- confidence
- requires_confirmation

Eval:
- expected vs actual

Verdict:
- PASS
- FAIL
- DA_VERIFICARE
