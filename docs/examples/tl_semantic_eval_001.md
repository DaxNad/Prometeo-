# TL semantic eval 001

Obiettivo: primo eval semantico controllato partendo dal micro-campione già sanificato.

Perimetro:
- nessun runtime
- nessun frontend
- nessuna AI esterna
- nessun file di pianificazione reale
- nessuna specifica
- nessuna immagine
- nessun codice reale

Input sanificato:
- articolo: ITEM_A
- stazioni: STATION_Z1, STATION_CP
- componente condiviso: COMP_SHARED_01

Domanda TL sanificata:
Dato ITEM_A con passaggio su STATION_Z1 e chiusura obbligatoria su STATION_CP, qual è la risposta operativa corretta?

Risposta attesa:
Controllare prima il completamento su STATION_CP, verificare il carico su STATION_Z1 e non alzare criticità se non esiste un evento bloccante.

Stato: TL_SEMANTIC_EVAL_READY
