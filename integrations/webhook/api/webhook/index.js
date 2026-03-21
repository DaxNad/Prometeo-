import crypto from "crypto";

// ---- utility: leggi il body RAW (Buffer), non JSON
function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", c => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

export default async function handler(req, res) {
  // Health check rapido
  if (req.method === "GET") return res.status(200).send("OK");
  if (req.method !== "POST") return res.status(405).send("Method Not Allowed");

  const secret = process.env.WEBHOOK_SECRET || "";
  const event  = String(req.headers["x-github-event"] || "");
  const sigHdr = String(req.headers["x-hub-signature-256"] || "");

  // 1) leggo i byte RAW così come arrivano da GitHub
  const raw = await readRawBody(req);

  // 2) calcolo la firma attesa
  const expected =
    "sha256=" + crypto.createHmac("sha256", secret).update(raw).digest("hex");

  // ---- LOG di debug (rimetti a 12-18 caratteri se vuoi)
  console.log("sigHdr:", sigHdr || "<missing>");
  console.log("expected:", expected);

  // 3) se manca l’header, errore
  if (!sigHdr) return res.status(401).send("Missing signature header");
  
if (process.env.SKIP_VERIFY === "1") {
  console.log("verify:SKIPPED");
} else {
  const ok =
    sigHdr.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sigHdr), Buffer.from(expected));
  if (!ok) return res.status(401).send("Invalid signature");
}

  // 4) confronto a tempo costante
  const ok =
    sigHdr.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sigHdr), Buffer.from(expected));

  if (!ok) return res.status(401).send("Invalid signature");

  // 5) Se la firma è ok, ora posso parse-are il JSON
  const payload = JSON.parse(raw.toString("utf8"));

  // Gestione eventi base
  if (event === "ping") {
    return res.status(200).json({ ok: true, event: "ping" });
  }

  if (event === "push") {
    // qui puoi fare la tua logica
    return res.status(200).json({ ok: true, event: "push" });
  }

  // default: 200 per non far riprovare GitHub
  return res.status(200).json({ ok: true, event });
}

// *** importantissimo: disabilita il body parser ***
export const config = { api: { bodyParser: false } };
