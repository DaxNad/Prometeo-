from __future__ import annotations

import re

OPERATIONAL_MATCH_WEIGHT: float = 0.15
SUPPLIER_MATCH_WEIGHT: float = 0.15
CUSTOMER_MATCH_WEIGHT: float = 0.15
MARKETING_MATCH_WEIGHT: float = 0.12
FOMO_MATCH_WEIGHT: float = 0.18
TRIAL_MATCH_WEIGHT: float = 0.15
URGENCY_MATCH_WEIGHT: float = 0.08
CTA_MATCH_WEIGHT: float = 0.08
PHISHING_INDICATOR_WEIGHT: float = 0.25
CREDENTIAL_REQUEST_WEIGHT: float = 0.30
UNSUBSCRIBE_MATCH_WEIGHT: float = 0.15
SUSPICIOUS_URL_WEIGHT: float = 0.25
SENDER_DOMAIN_MISMATCH_WEIGHT: float = 0.15

PHISHING_THRESHOLD: float = 0.45
OPERATIONAL_THRESHOLD: float = 0.38
SUPPLIER_THRESHOLD: float = 0.30
CUSTOMER_THRESHOLD: float = 0.30
GREY_MARKETING_THRESHOLD: float = 0.38
MARKETING_THRESHOLD: float = 0.25
MINIMUM_WORDS_FOR_CLASSIFICATION: int = 5

RISK_SCORE_RANGE: dict[str, tuple[float, float]] = {
    "phishing": (0.70, 0.95),
    "grey_marketing": (0.35, 0.60),
    "marketing": (0.05, 0.20),
    "supplier": (0.00, 0.10),
    "customer": (0.00, 0.10),
    "operational": (0.00, 0.05),
    "unknown": (0.15, 0.25),
}

OPERATIONAL_KEYWORDS: frozenset[str] = frozenset([
    "ordine", "ordini", "articolo", "articoli",
    "fase", "fasi", "postazione", "postazioni",
    "componente", "componenti", "assemblaggio",
    "produzione", "reparto", "turno",
    "saturazione", "segnalazione operativa",
    "team leader", "piano di turno",
    "lotto", "batch", "quantità",
    "priorità operativa", "blocco produttivo",
    "picking", "kit", "prelievo",
    "bolla", "ddt", "documento di trasporto",
    "zaw", "pidmill", "henn", "ultrasuoni", "guaine",
    "work order", "production order", "assembly",
    "bill of materials", "shop floor",
])

SUPPLIER_KEYWORDS: frozenset[str] = frozenset([
    "fornitore", "fornitori",
    "ordine di acquisto", "conferma ordine fornitore",
    "lead time", "preventivo",
    "consegna prevista", "data di consegna fornitore",
    "nota credito", "ordine quadro", "accordo fornitura",
    "spedizioniere", "tracking spedizione",
    "purchase order", "supplier", "vendor",
    "delivery confirmation", "invoice", "pro forma",
    "estimated delivery", "dispatch notice",
    "goods received", "po confirmation",
])

CUSTOMER_KEYWORDS: frozenset[str] = frozenset([
    "cliente", "clienti",
    "richiesta cliente", "urgenza cliente",
    "data di consegna richiesta", "ordine cliente",
    "numero ordine cliente", "conferma spedizione cliente",
    "ritardo consegna", "sollecito", "reclamo",
    "customer order", "delivery date request",
    "shipment confirmation", "order status",
    "order number", "client request",
    "delivery delay", "complaint",
])

MARKETING_KEYWORDS: frozenset[str] = frozenset([
    "offerta", "offerte", "sconto", "sconti",
    "promozione", "promozioni", "coupon",
    "newsletter", "risparmia",
    "abbonamento", "abbonamenti",
    "piano premium", "upgrade",
    "licenza software", "campagna marketing",
    "deal", "discount", "special offer",
    "subscription", "upgrade plan",
    "free plan", "pricing plan",
    "promotional", "advertisement",
])

FOMO_PHRASES: frozenset[str] = frozenset([
    "solo oggi", "offerta limitata", "ultimi posti",
    "non perdere", "scade il", "affrettati",
    "per un periodo limitato", "offerta valida fino al",
    "solo per oggi", "ultima occasione",
    "offerta esclusiva", "disponibilità limitata",
    "last chance", "limited time", "expires soon",
    "act now", "don't miss", "hurry",
    "ending soon", "today only",
    "limited offer", "don't wait", "selling fast",
    "while supplies last",
])

TRIAL_LANGUAGE: frozenset[str] = frozenset([
    "prova gratuita", "senza carta di credito",
    "senza impegno", "demo gratuita",
    "accesso gratuito", "piano gratuito",
    "inizia gratis", "mesi gratis", "giorni gratis",
    "free trial", "without credit card",
    "no credit card", "try for free",
    "start free", "no commitment",
    "30-day free", "14-day free", "7-day free",
    "try it free", "free access",
])

URGENCY_LANGUAGE: frozenset[str] = frozenset([
    "urgente", "subito", "immediatamente",
    "non aspettare", "entro oggi", "entro domani",
    "scade oggi", "entro le ore",
    "urgent", "immediately", "right now",
    "asap", "do it now", "act immediately",
    "today only", "expires today",
])

CTA_LANGUAGE: frozenset[str] = frozenset([
    "clicca qui", "scopri di più", "inizia ora",
    "registrati ora", "scarica ora", "acquista ora",
    "prenota ora", "iscriviti ora", "accedi ora",
    "click here", "get started", "sign up now",
    "try now", "download now", "buy now",
    "book now", "subscribe now", "login now",
    "start now", "join now",
])

PHISHING_INDICATORS: frozenset[str] = frozenset([
    "verifica il tuo account", "conferma la tua identità",
    "il tuo account è stato sospeso",
    "attività sospetta rilevata",
    "accedi per verificare",
    "clicca per evitare la sospensione",
    "il tuo accesso è stato bloccato",
    "azione immediata richiesta",
    "conferma i tuoi dati di sicurezza",
    "your account has been suspended",
    "unusual activity detected",
    "verify your identity",
    "your account will be closed",
    "suspicious activity",
    "account verification required",
    "immediate action required",
    "we detected unusual",
    "your account is at risk",
    "security alert",
])

CREDENTIAL_REQUESTS: frozenset[str] = frozenset([
    "inserisci le tue credenziali",
    "inserisci la tua password",
    "aggiorna il tuo metodo di pagamento",
    "conferma i tuoi dati di accesso",
    "inserisci il tuo codice di accesso",
    "enter your password", "enter your username",
    "update your payment", "reset your password",
    "provide your credentials",
    "confirm your login", "verify your password",
    "re-enter your password",
    "update billing information",
    "enter your credit card",
])

UNSUBSCRIBE_MARKERS: frozenset[str] = frozenset([
    "cancella iscrizione", "annulla la sottoscrizione",
    "non ricevere più", "per non ricevere altre email",
    "unsubscribe", "opt-out", "opt out",
    "remove me from", "manage email preferences",
    "email preferences", "manage preferences",
])

SUSPICIOUS_URL_RE: re.Pattern[str] = re.compile(
    r"(?:"
    r"https?://(?:\d{1,3}\.){3}\d{1,3}"
    r"|http://"
    r"|bit\.ly/"
    r"|tinyurl\.com/"
    r"|goo\.gl/"
    r"|t\.co/"
    r"|ow\.ly/"
    r"|rb\.gy/"
    r")",
    re.IGNORECASE,
)

SUSPICIOUS_SENDER_RE: re.Pattern[str] = re.compile(
    r"(?:"
    r"@(?:\d{1,3}\.){3}\d{1,3}$"
    r"|@[^@]+\.(?:xyz|tk|ml|cf|gq|ga)$"
    r")",
    re.IGNORECASE,
)
