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

## AI Provider Independence

PROMETEO non deve essere OpenAI-powered, Claude-powered, Ollama-powered o dipendente da un singolo provider AI.

PROMETEO deve trattare ogni modello AI come modulo sostituibile.

Architettura di principio:

PROMETEO
→ AI Router
→ provider esterno
→ provider alternativo
→ Local LLM
→ fallback deterministico
→ no-AI fallback

Il dominio, le fonti, le regole, il retrieval, gli eval e la decisione TL devono restare validi anche se il provider AI cambia.

Motivo strategico:

- evitare lock-in tecnico;
- contenere rischio di aumento costi AI;
- ridurre dipendenza da inferenza continua;
- permettere uso locale quando opportuno;
- mantenere PROMETEO operativo anche con AI ridotta o assente;
- proteggere il sistema da cambi commerciali dei provider.

Regola:

nessuna capability PROMETEO deve richiedere un provider AI specifico per esistere.

Un provider puo migliorare velocita, qualita o comodita.

Non deve diventare fonte di verita, prerequisito operativo o punto singolo di fallimento.


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
