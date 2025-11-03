/**
 * GEKO - Test Runtime Frontend
 * Verifica che il server frontend sia raggiungibile su http://localhost:5173
 */

import http from "http";

console.log("=".repeat(60));
console.log("[*] Test Runtime Frontend - GEKO");
console.log("=".repeat(60));
console.log("\n[*] Testando apertura http://localhost:5173 ...\n");

const options = {
  hostname: "localhost",
  port: 5173,
  path: "/",
  method: "GET",
  timeout: 5000,
};

const req = http.request(options, (res) => {
  console.log(`[OK] Server frontend attivo`);
  console.log(`    Status Code: ${res.statusCode}`);
  console.log(`    Headers: ${JSON.stringify(res.headers, null, 2)}`);

  let data = "";
  res.on("data", (chunk) => {
    data += chunk.toString();
  });

  res.on("end", () => {
    if (data.length > 0) {
      console.log(`    Response length: ${data.length} bytes`);
      if (data.includes("<html") || data.includes("<!DOCTYPE")) {
        console.log(`    [OK] Risposta HTML valida`);
      } else if (data.includes("<!doctype html")) {
        console.log(`    [OK] Risposta HTML valida (doctype)`);
      }
    }
    console.log("\n[OK] Test runtime completato con successo!");
    process.exit(0);
  });
});

req.on("error", (err) => {
  console.error(`[ERROR] Server frontend non raggiungibile`);
  console.error(`    Errore: ${err.message}`);
  console.error("\n[INFO] Possibili cause:");
  console.error("    1. Il server dev non è avviato (esegui: npm run dev)");
  console.error("    2. La porta 5173 è occupata da un altro processo");
  console.error("    3. Il server è su una porta diversa");
  console.error("\n[INFO] Per avviare il server:");
  console.error("    npm run dev");
  process.exit(1);
});

req.on("timeout", () => {
  console.error(`[ERROR] Timeout connessione al server`);
  req.destroy();
  process.exit(1);
});

req.end();

