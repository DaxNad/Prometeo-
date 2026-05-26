# TL PATTERN — ZAW1 / ZAW2 NON INTERCAMBIABILI

## STATUS

CERTO — CONFIRMED_BY_TL

## PATTERN TL

Scenario: distinzione operativa ZAW1 e ZAW2

Codice/i: multipli

Famiglia: articoli con passaggi ZAW

Postazione/i: ZAW1, ZAW2

Osservazione reale: ZAW1 e ZAW2 non sono intercambiabili. Un doppio passaggio ZAW non implica automaticamente ZAW2.

Regola pratica TL: non dedurre ZAW2 da doppio passaggio ZAW. ZAW2 va usata solo quando configurazione reale, specifica o conferma TL indicano manicotto, plastica, tre vie, giunzione multipla o caso equivalente.

Quando vale: codici con innesti rapidi semplici, doppio passaggio ZAW o crimpature non confermate come ZAW2.

Quando NON vale: configurazioni confermate ZAW2, tre vie, manicotti, giunzioni multiple, plastiche o casi espliciti da specifica/TL.

Impatto su 100 pz/testa: evita assegnazione errata di postazione e riduce perdite da routing sbagliato.

Impatto su delega operatori: assegna il codice a operatore/postazione compatibile con ZAW reale, non con inferenza automatica.

Confidenza TL: CERTO

## RUNTIME RULE

PROMETEO deve classificare ogni inferenza automatica ZAW2 non confermata come DA_VERIFICARE.

## LINKED IMPERATIVE

Questo pattern supporta PROMETEO PATTERN LEARNING e riduce arretratezza rispetto alla pratica produttiva reale.
