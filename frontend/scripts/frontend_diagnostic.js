import { execSync } from "child_process";
import fs from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const frontendRoot = join(__dirname, "..");

function logResult(title, result) {
  console.log(`\n✅ ${title}:\n${result}`);
}

function logError(title, error) {
  console.error(`\n❌ ${title}:\n${error.message || error}`);
}

function logWarning(title, message) {
  console.warn(`\n⚠️  ${title}:\n${message}`);
}

console.log('='.repeat(60));
console.log('🔍 DIAGNOSTICA COMPLETA FRONTEND GEKO');
console.log('='.repeat(60));

const report = [];

// 1. Verifica versioni Node.js e npm
console.log('\n1️⃣ Verifica ambiente Node.js...');
try {
  const nodeVer = execSync("node -v", { encoding: 'utf8' }).toString().trim();
  const npmVer = execSync("npm -v", { encoding: 'utf8' }).toString().trim();
  logResult("Versioni Node.js / npm", `Node: ${nodeVer}\nNPM: ${npmVer}`);
  report.push(`✅ Node.js: ${nodeVer}`);
  report.push(`✅ npm: ${npmVer}`);
} catch (e) {
  logError("Verifica Node/NPM", e);
  report.push(`❌ Errore verifica Node/NPM: ${e.message}`);
}

// 2. Verifica package.json
console.log('\n2️⃣ Verifica package.json...');
try {
  const packageJsonPath = join(frontendRoot, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    logResult("package.json", "Trovato e valido");
    report.push(`✅ package.json valido`);
    
    // Verifica script
    if (packageJson.scripts?.dev) {
      report.push(`✅ Script 'dev' presente`);
    } else {
      logWarning("Script dev", "Script 'dev' non trovato in package.json");
      report.push(`⚠️  Script 'dev' mancante`);
    }
  } else {
    logError("package.json", new Error("File non trovato"));
    report.push(`❌ package.json non trovato`);
  }
} catch (e) {
  logError("Verifica package.json", e);
  report.push(`❌ Errore package.json: ${e.message}`);
}

// 3. Verifica node_modules
console.log('\n3️⃣ Verifica node_modules...');
try {
  const nodeModulesPath = join(frontendRoot, 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    const stats = fs.statSync(nodeModulesPath);
    logResult("node_modules", "Presente");
    report.push(`✅ node_modules presente`);
    
    // Verifica dipendenze critiche
    const criticalDeps = ['react', 'react-dom', 'vite'];
    const missing = criticalDeps.filter(dep => {
      return !fs.existsSync(join(nodeModulesPath, dep));
    });
    
    if (missing.length > 0) {
      logWarning("Dipendenze mancanti", `Mancanti: ${missing.join(', ')}`);
      report.push(`⚠️  Dipendenze mancanti: ${missing.join(', ')}`);
    } else {
      report.push(`✅ Dipendenze critiche presenti`);
    }
  } else {
    logWarning("node_modules", "Non presente - sarà necessario eseguire npm install");
    report.push(`⚠️  node_modules non presente`);
  }
} catch (e) {
  logError("Verifica node_modules", e);
  report.push(`❌ Errore verifica node_modules: ${e.message}`);
}

// 4. Installazione dipendenze (se necessario)
console.log('\n4️⃣ Installazione dipendenze...');
try {
  process.chdir(frontendRoot);
  execSync("npm install", { stdio: "inherit", encoding: 'utf8' });
  logResult("Installazione dipendenze", "Completata con successo");
  report.push(`✅ Installazione dipendenze completata`);
} catch (e) {
  logError("Installazione dipendenze", e);
  report.push(`❌ Errore installazione: ${e.message}`);
}

// 5. Verifica struttura file
console.log('\n5️⃣ Verifica struttura file...');
try {
  const requiredFiles = [
    'src/main.jsx',
    'src/App.jsx',
    'src/index.css',
    'index.html',
    'vite.config.js'
  ];
  
  const missingFiles = requiredFiles.filter(file => {
    return !fs.existsSync(join(frontendRoot, file));
  });
  
  if (missingFiles.length > 0) {
    logError("File mancanti", `Mancanti: ${missingFiles.join(', ')}`);
    report.push(`❌ File mancanti: ${missingFiles.join(', ')}`);
  } else {
    logResult("Struttura file", "Tutti i file necessari presenti");
    report.push(`✅ Struttura file completa`);
  }
} catch (e) {
  logError("Verifica struttura file", e);
  report.push(`❌ Errore verifica file: ${e.message}`);
}

// 6. Test build
console.log('\n6️⃣ Test build frontend...');
try {
  process.chdir(frontendRoot);
  execSync("npm run build", { stdio: "inherit", encoding: 'utf8' });
  logResult("Build Frontend", "Eseguita correttamente");
  report.push(`✅ Build completata con successo`);
  
  // Verifica dist
  const distPath = join(frontendRoot, 'dist');
  if (fs.existsSync(distPath)) {
    const distFiles = fs.readdirSync(distPath);
    report.push(`✅ Cartella dist creata con ${distFiles.length} file`);
  }
} catch (e) {
  logError("Build Frontend", e);
  report.push(`❌ Errore build: ${e.message}`);
}

// 7. Verifica porta
console.log('\n7️⃣ Verifica porta 5173...');
try {
  const output = execSync("netstat -ano | findstr :5173", { encoding: 'utf8' }).toString();
  if (output.includes("LISTENING")) {
    logWarning("Porta 5173", "Porta già in uso da un altro processo");
    report.push(`⚠️  Porta 5173 già in uso`);
    
    // Estrai PID
    const lines = output.split('\n');
    const listeningLine = lines.find(line => line.includes('LISTENING'));
    if (listeningLine) {
      const pid = listeningLine.trim().split(/\s+/).pop();
      report.push(`   PID processo: ${pid}`);
    }
  } else {
    logResult("Porta 5173", "Libera e disponibile");
    report.push(`✅ Porta 5173 libera`);
  }
} catch (e) {
  // Se non trova nulla, la porta è libera
  logResult("Porta 5173", "Libera (nessun processo trovato)");
  report.push(`✅ Porta 5173 libera`);
}

// 8. Verifica configurazione Vite
console.log('\n8️⃣ Verifica configurazione Vite...');
try {
  const viteConfigPath = join(frontendRoot, 'vite.config.js');
  if (fs.existsSync(viteConfigPath)) {
    const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');
    logResult("vite.config.js", "Presente e valido");
    report.push(`✅ vite.config.js presente`);
    
    if (viteConfig.includes('port: 5173')) {
      report.push(`✅ Porta 5173 configurata in vite.config.js`);
    }
  } else {
    logError("vite.config.js", new Error("File non trovato"));
    report.push(`❌ vite.config.js non trovato`);
  }
} catch (e) {
  logError("Verifica vite.config.js", e);
  report.push(`❌ Errore vite.config.js: ${e.message}`);
}

// 9. Genera report
console.log('\n9️⃣ Generazione report...');
try {
  const reportPath = join(frontendRoot, 'diagnostic_report_frontend.txt');
  const reportContent = [
    '='.repeat(60),
    'REPORT DIAGNOSTICA FRONTEND GEKO',
    new Date().toISOString(),
    '='.repeat(60),
    '',
    ...report,
    '',
    '='.repeat(60),
    'Fine report',
    '='.repeat(60)
  ].join('\n');
  
  fs.writeFileSync(reportPath, reportContent);
  logResult("Report generato", `File: ${reportPath}`);
} catch (e) {
  logError("Generazione report", e);
}

// Riepilogo finale
console.log('\n' + '='.repeat(60));
console.log('📊 RIEPILOGO DIAGNOSTICA');
console.log('='.repeat(60));

const errors = report.filter(r => r.startsWith('❌')).length;
const warnings = report.filter(r => r.startsWith('⚠️')).length;
const successes = report.filter(r => r.startsWith('✅')).length;

console.log(`✅ Successi: ${successes}`);
console.log(`⚠️  Avvisi: ${warnings}`);
console.log(`❌ Errori: ${errors}`);

if (errors === 0) {
  console.log('\n🎉 Tutti i controlli sono passati! Il frontend dovrebbe funzionare correttamente.');
  console.log('\n💡 Per avviare il server dev:');
  console.log('   npm run dev');
  console.log('\n💡 Poi apri nel browser:');
  console.log('   http://localhost:5173');
} else {
  console.log('\n⚠️  Ci sono problemi che devono essere risolti prima di avviare il server.');
}

console.log('\n' + '='.repeat(60));

