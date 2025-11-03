/**
 * GEKO – Fase 1.3 Diagnostica Completa Frontend
 * Autore: Sistema Cursor
 * Descrizione: verifica integrità e funzionamento ambiente React/Vite
 */

import { execSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import http from "http";

const report = {
  timestamp: new Date().toISOString(),
  node: null,
  npm: null,
  vite: null,
  deps: null,
  build: null,
  port5173: null,
  backendCheck: null,
  configFiles: {},
  summary: [],
  status: "UNKNOWN",
};

function run(cmd) {
  try {
    return execSync(cmd, { encoding: "utf8", stdio: "pipe" }).trim();
  } catch (err) {
    return `ERROR: ${err.message}`;
  }
}

function checkPort(port) {
  try {
    const result = run(`netstat -ano | findstr :${port}`);
    if (result && !result.includes("ERROR")) {
      return {
        status: "occupied",
        details: result,
      };
    }
    return {
      status: "free",
      details: "Porta libera",
    };
  } catch (err) {
    return {
      status: "unknown",
      details: err.message,
    };
  }
}

function checkBackendConnection() {
  return new Promise((resolve) => {
    const req = http.get("http://localhost:8000/health", (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        if (res.statusCode === 200) {
          resolve({
            status: "OK",
            message: "Backend raggiungibile",
            statusCode: res.statusCode,
          });
        } else {
          resolve({
            status: "WARNING",
            message: `Backend risponde con status ${res.statusCode}`,
            statusCode: res.statusCode,
          });
        }
      });
    });

    req.on("error", (err) => {
      resolve({
        status: "ERROR",
        message: `Backend non raggiungibile: ${err.message}`,
      });
    });

    req.setTimeout(3000, () => {
      req.destroy();
      resolve({
        status: "ERROR",
        message: "Timeout connessione backend",
      });
    });
  });
}

async function main() {
  console.log("=".repeat(60));
  console.log("[*] GEKO - Fase 1.3 Diagnostica Completa Frontend");
  console.log("=".repeat(60));
  console.log(`Data/ora: ${report.timestamp}\n`);

  // 1️⃣ Controllo versioni
  console.log("[1] Verifica versioni Node.js / npm / Vite...");
  report.node = run("node -v");
  report.npm = run("npm -v");
  
  try {
    const viteVersion = run("npm list vite --depth=0");
    if (viteVersion.includes("ERROR")) {
      report.vite = "NON INSTALLATO";
    } else {
      const match = viteVersion.match(/vite@([\d.]+)/);
      report.vite = match ? match[1] : viteVersion;
    }
  } catch {
    report.vite = "ERRORE";
  }

  console.log(`    Node.js: ${report.node}`);
  console.log(`    npm: ${report.npm}`);
  console.log(`    Vite: ${report.vite}`);

  // 2️⃣ Verifica file di configurazione
  console.log("\n[2] Verifica file di configurazione...");
  const configFiles = [
    "package.json",
    "vite.config.js",
    "tsconfig.json",
    ".env",
    ".env.local",
  ];

  configFiles.forEach((file) => {
    const filePath = path.join(process.cwd(), file);
    if (fs.existsSync(filePath)) {
      report.configFiles[file] = "presente";
      console.log(`    [OK] ${file}`);
    } else {
      report.configFiles[file] = "mancante";
      console.log(`    [WARN] ${file} non trovato`);
    }
  });

  // 3️⃣ Verifica dipendenze
  console.log("\n[3] Verifica dipendenze installate...");
  try {
    const depsCheck = run("npm list --depth=0 2>&1");
    if (depsCheck.includes("missing") || depsCheck.includes("ERR!")) {
      report.deps = {
        status: "ERROR",
        message: "Dipendenze mancanti o errori nell'installazione",
        details: depsCheck.substring(0, 500),
      };
      console.log("    [ERROR] Problemi con le dipendenze");
    } else {
      const depCount = (depsCheck.match(/├─/g) || []).length;
      report.deps = {
        status: "OK",
        message: `Dipendenze installate correttamente`,
        count: depCount,
      };
      console.log(`    [OK] ${depCount} dipendenze installate`);
    }
  } catch (err) {
    report.deps = {
      status: "ERROR",
      message: err.message,
    };
    console.log(`    [ERROR] ${err.message}`);
  }

  // 4️⃣ Test build
  console.log("\n[4] Test build frontend...");
  try {
    const buildResult = run("npm run build 2>&1");
    if (buildResult.includes("built in") || buildResult.includes("dist/index.html")) {
      report.build = {
        status: "OK",
        message: "Build completata con successo",
        details: buildResult.substring(buildResult.length - 200),
      };
      console.log("    [OK] Build completata");

      // Verifica cartella dist
      const distPath = path.join(process.cwd(), "dist");
      if (fs.existsSync(distPath)) {
        const files = fs.readdirSync(distPath);
        report.build.filesCount = files.length;
        console.log(`    [OK] Cartella dist creata con ${files.length} file`);
      }
    } else if (buildResult.includes("ERROR")) {
      report.build = {
        status: "ERROR",
        message: "Errore durante la build",
        details: buildResult.substring(0, 500),
      };
      console.log("    [ERROR] Build fallita");
    } else {
      report.build = {
        status: "WARNING",
        message: "Build completata con warning",
        details: buildResult.substring(0, 500),
      };
      console.log("    [WARN] Build con warning");
    }
  } catch (err) {
    report.build = {
      status: "ERROR",
      message: err.message,
    };
    console.log(`    [ERROR] ${err.message}`);
  }

  // 5️⃣ Verifica porta 5173
  console.log("\n[5] Verifica porta 5173...");
  report.port5173 = checkPort(5173);
  if (report.port5173.status === "occupied") {
    console.log("    [WARN] Porta 5173 occupata");
  } else {
    console.log("    [OK] Porta 5173 libera");
  }

  // 6️⃣ Verifica comunicazione backend
  console.log("\n[6] Verifica connessione backend (http://localhost:8000/health)...");
  report.backendCheck = await checkBackendConnection();
  if (report.backendCheck.status === "OK") {
    console.log(`    [OK] ${report.backendCheck.message}`);
  } else {
    console.log(`    [${report.backendCheck.status}] ${report.backendCheck.message}`);
  }

  // 7️⃣ Verifica vite.config.js
  console.log("\n[7] Verifica configurazione Vite...");
  const viteConfigPath = path.join(process.cwd(), "vite.config.js");
  if (fs.existsSync(viteConfigPath)) {
    try {
      const viteConfig = fs.readFileSync(viteConfigPath, "utf8");
      if (viteConfig.includes("port: 5173")) {
        report.viteConfig = {
          status: "OK",
          port: 5173,
          message: "Porta 5173 configurata",
        };
        console.log("    [OK] vite.config.js valido con porta 5173");
      } else {
        report.viteConfig = {
          status: "WARNING",
          message: "Porta non esplicitamente configurata",
        };
        console.log("    [WARN] Porta non configurata esplicitamente");
      }
    } catch (err) {
      report.viteConfig = {
        status: "ERROR",
        message: err.message,
      };
      console.log(`    [ERROR] ${err.message}`);
    }
  } else {
    report.viteConfig = {
      status: "ERROR",
      message: "vite.config.js non trovato",
    };
    console.log("    [ERROR] vite.config.js non trovato");
  }

  // 8️⃣ Generazione summary e status finale
  console.log("\n[8] Generazione summary...");
  const errors = [];
  const warnings = [];
  const successes = [];

  if (report.node.includes("ERROR")) errors.push("Node.js non disponibile");
  else successes.push("Node.js OK");

  if (report.npm.includes("ERROR")) errors.push("npm non disponibile");
  else successes.push("npm OK");

  if (report.vite === "NON INSTALLATO" || report.vite === "ERRORE") {
    errors.push("Vite non installato");
  } else {
    successes.push("Vite installato");
  }

  if (report.deps?.status === "ERROR") errors.push("Problemi con dipendenze");
  else if (report.deps?.status === "OK") successes.push("Dipendenze OK");

  if (report.build?.status === "ERROR") errors.push("Build fallita");
  else if (report.build?.status === "OK") successes.push("Build OK");

  if (report.port5173.status === "occupied") warnings.push("Porta 5173 occupata");
  else successes.push("Porta 5173 libera");

  if (report.backendCheck.status === "ERROR") warnings.push("Backend non raggiungibile");
  else if (report.backendCheck.status === "OK") successes.push("Backend OK");

  report.summary = {
    successes,
    warnings,
    errors,
  };

  // Determina status finale
  if (errors.length > 0) {
    report.status = "ERROR";
  } else if (warnings.length > 0) {
    report.status = "WARNING";
  } else {
    report.status = "OK";
  }

  // 9️⃣ Generazione report finale
  console.log("\n[9] Generazione report...");
  const reportPath = path.join(process.cwd(), "diagnostic_report_frontend_full.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // Stampa riepilogo
  console.log("\n" + "=".repeat(60));
  console.log("[*] RIEPILOGO DIAGNOSTICA");
  console.log("=".repeat(60));
  console.log(`Status: ${report.status}`);
  console.log(`\nSuccessi: ${successes.length}`);
  successes.forEach((s) => console.log(`  [OK] ${s}`));
  
  if (warnings.length > 0) {
    console.log(`\nAvvisi: ${warnings.length}`);
    warnings.forEach((w) => console.log(`  [WARN] ${w}`));
  }
  
  if (errors.length > 0) {
    console.log(`\nErrori: ${errors.length}`);
    errors.forEach((e) => console.log(`  [ERROR] ${e}`));
  }

  console.log(`\n[OK] Diagnostica frontend completata. Report salvato in: ${reportPath}`);

  return report;
}

main().catch((err) => {
  console.error("[ERROR] Errore durante diagnostica:", err);
  process.exit(1);
});

