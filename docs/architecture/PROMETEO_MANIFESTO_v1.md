# PROMETEO — MANIFESTO TECNICO PERMANENTE v1
stato: attivo
validità: permanente
ambito: architettura, sviluppo, evoluzione prodotto

---

# 1. IDENTITÀ DEL SISTEMA

PROMETEO è una piattaforma semantica industriale progettata per supportare il Team Leader nella costruzione della strategia operativa di reparto.

PROMETEO non è:
- un ERP
- un MES tradizionale
- un semplice gestionale
- un database con interfaccia

PROMETEO è:
- un orchestratore semantico
- un interprete del dominio produttivo reale
- un sistema di continuità cognitiva tra turni
- un motore di supporto decisionale spiegabile
- un layer intelligente tra dati, vincoli e azioni operative

---

# 2. PRINCIPIO GUIDA ASSOLUTO

PROMETEO deve evolvere come sistema:

- ad alte prestazioni
- unico per profondità semantica
- modulare per natura
- componibile per sezioni
- adattabile a contesti industriali diversi
- coerente con il dominio reale
- spiegabile nelle decisioni
- robusto nel tempo

Ogni evoluzione deve aumentare:
- comprensione del dominio
- stabilità architetturale
- riusabilità futura
- utilità operativa reale

---

# 3. CENTRALITÀ DEL TEAM LEADER

PROMETEO non sostituisce il Team Leader.

PROMETEO amplifica la capacità del Team Leader di:

- leggere il disegno
- riconoscere famiglie tecniche
- prevedere colli di bottiglia
- bilanciare le postazioni
- anticipare conflitti tra articoli
- organizzare la sequenza produttiva
- mantenere continuità tra turni

Il disegno tecnico è la chiave logica primaria della strategia.

PROMETEO deve sempre rispettare questa gerarchia:

1. specifica reale di finitura
2. struttura componenti reale (BOM)
3. conoscenza operativa Team Leader
4. inferenza del modello

---

# 4. INTELLIGENZA SEMANTICA

PROMETEO deve comprendere il significato operativo dei dati.

Non basta memorizzare:
- codici
- quantità
- postazioni

PROMETEO deve interpretare:

- comportamento produttivo
- dipendenze tra componenti
- compatibilità tra articoli
- criticità condivise
- vincoli di sequenza
- effetti sui turni successivi
- priorità reali di reparto

Ogni entità deve poter essere classificata come:

CERTO
INFERITO
DA VERIFICARE

Nessun dato inferito può essere trattato come definitivo senza controllo incrociato.

---

# 5. ARCHITETTURA MODULARE

PROMETEO deve essere costruito come sistema a moduli separabili.

Moduli principali:

CORE
modello dominio
Order
ProductionEvent
Station
Phase
Rule
vincoli

SMF BRIDGE
raccolta dati reale
normalizzazione
ingestione
sincronizzazione

ATLAS ENGINE
analisi
interpretazione
suggerimenti
merge decisionale

PLANNER
costruzione sequenze operative
strategia turno
bilanciamento postazioni

REGISTRY SEMANTICO
famiglie tecniche
compatibilità
comportamenti produttivi
mapping disegni

AUDIT
log strutturati
tracciabilità modifiche
storia decisioni

INTERFACCIA OPERATIVA
PWA
dashboard
input operatore
visualizzazione strategia

INTEGRAZIONE ESTERNA
ERP
MES
API
import/export

VOICE LAYER (futuro)
comandi vocali
COMANDO / NOTE
interazione naturale TL

Ogni modulo deve poter evolvere senza rompere gli altri.

---

# 6. COERENZA ARCHITETTURALE

PROMETEO non deve generare biforcazioni incoerenti tra:

smf_core
backend
planner
registry
frontend

Il modello dominio deve restare unico.

Order è l'aggregato centrale.

ProductionEvent è la traccia reale del processo.

Route definisce possibilità.
Event registra realtà.

---

# 7. PRIORITÀ OPERATIVA PERMANENTE

ordine invariabile:

1. bilanciamento postazioni
2. scadenze cliente
3. lotti coerenti
4. continuità tra turni
5. riduzione colli di bottiglia
6. cartellinatura subordinata

PROMETEO deve sempre favorire strategie che:

evitano accumuli su postazioni critiche
evitano scarico problemi sul turno successivo
favoriscono stabilità del flusso
rendono prevedibile il carico

---

# 8. GESTIONE COMPONENTI CONDIVISI

componenti comuni tra articoli diversi sono vincoli strategici.

esempio:
O-ring
rapidi
plastiche condivise
connettori comuni
manicotti

un singolo componente può bloccare più articoli.

PROMETEO deve modellare questa dipendenza.

---

# 9. EXPLAINABILITY

ogni suggerimento prodotto deve poter spiegare:

perché
quali vincoli hanno influito
quali conflitti sono stati evitati
quali priorità sono state considerate
quali moduli concordano
quali moduli sono in disaccordo

output minimo atteso:

esito
ALLOW
BLOCK
DEFER
BOOST

priorità
vincoli attivi
motivazione sintetica

---

# 10. EDGE + BACKEND

PROMETEO deve funzionare anche in contesti con connettività limitata.

principi:

edge operativo locale
backend come stabilizzatore dominio
sincronizzazione quando possibile
continuità operativa garantita

SMF nasce come ponte dati reale, non come verità assoluta.

---

# 11. EVOLUZIONE CONTROLLATA

ordine stabile di sviluppo:

1 guard rail anti-rottura
2 densificazione dominio reale
3 consolidamento registry semantico
4 planner spiegabile
5 interfaccia utile al Team Leader
6 integrazione sistemi esterni

nessuna nuova funzione deve:

rompere coerenza dominio
duplicare logiche esistenti
introdurre dipendenze inutili
creare scorciatoie non riusabili

---

# 12. CRITERI DI VALIDAZIONE DI UNA NUOVA FUNZIONE

una modifica è coerente solo se aumenta almeno uno di:

comprensione dominio
stabilità architettura
riusabilità futura
intelligenza semantica
utilità reale per il Team Leader

se non migliora uno di questi punti, non è prioritaria.

---

# 13. OBIETTIVO STRATEGICO

costruire una piattaforma semantica industriale:

robusta
spiegabile
modulare
adattabile
riusabile
integrabile
utile al reparto reale
evolvibile nel tempo

PROMETEO deve diventare un sistema capace di:

interpretare il contesto produttivo
supportare decisioni operative
mantenere continuità cognitiva tra turni
ridurre attrito operativo
standardizzare la conoscenza del reparto

senza irrigidire il dominio reale.

---

# FINE MANIFESTO
