#!/usr/bin/env node
/**
 * Script diagnostico per il frontend Geko
 * Verifica tutti i possibili problemi che impediscono l'avvio
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const problems = [];
const warnings = [];

console.log('='.repeat(60));
console.log('🔍 DIAGNOSTICA FRONTEND GEKO');
console.log('='.repeat(60));
console.log();

// 1. Verifica esistenza package.json
console.log('1️⃣ Verifica file di configurazione...');
const packageJsonPath = path.join(__dirname, 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  problems.push('package.json non trovato');
} else {
  console.log('   ✓ package.json trovato');
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  // Verifica dipendenze
  const requiredDeps = [
    'react',
    'react-dom',
    'react-router-dom',
    'zustand',
    'axios',
    'framer-motion',
    'lucide-react'
  ];
  
  const missingDeps = requiredDeps.filter(dep => !pkg.dependencies?.[dep]);
  if (missingDeps.length > 0) {
    problems.push(`Dipendenze mancanti: ${missingDeps.join(', ')}`);
  } else {
    console.log('   ✓ Tutte le dipendenze richieste presenti in package.json');
  }
}

// 2. Verifica node_modules
console.log('\n2️⃣ Verifica dipendenze installate...');
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  problems.push('node_modules non trovato - eseguire "npm install"');
} else {
  console.log('   ✓ node_modules presente');
  
  // Verifica alcune dipendenze critiche
  const criticalDeps = ['react', 'react-dom', 'vite'];
  const missing = criticalDeps.filter(dep => {
    const depPath = path.join(nodeModulesPath, dep);
    return !fs.existsSync(depPath);
  });
  
  if (missing.length > 0) {
    problems.push(`Dipendenze critiche mancanti in node_modules: ${missing.join(', ')}`);
  } else {
    console.log('   ✓ Dipendenze critiche installate');
  }
}

// 3. Verifica struttura cartelle src
console.log('\n3️⃣ Verifica struttura progetto...');
const srcPath = path.join(__dirname, 'src');
if (!fs.existsSync(srcPath)) {
  problems.push('Cartella src non trovata');
} else {
  console.log('   ✓ Cartella src presente');
  
  const requiredFiles = [
    'main.jsx',
    'App.jsx',
    'index.css'
  ];
  
  const missingFiles = requiredFiles.filter(file => {
    return !fs.existsSync(path.join(srcPath, file));
  });
  
  if (missingFiles.length > 0) {
    problems.push(`File mancanti in src/: ${missingFiles.join(', ')}`);
  } else {
    console.log('   ✓ File principali presenti');
  }
  
  // Verifica cartelle
  const requiredDirs = ['components', 'pages', 'store', 'services'];
  const missingDirs = requiredDirs.filter(dir => {
    return !fs.existsSync(path.join(srcPath, dir));
  });
  
  if (missingDirs.length > 0) {
    warnings.push(`Cartelle mancanti (potrebbero essere create al primo avvio): ${missingDirs.join(', ')}`);
  } else {
    console.log('   ✓ Struttura cartelle corretta');
  }
}

// 4. Verifica vite.config.js
console.log('\n4️⃣ Verifica configurazione Vite...');
const viteConfigPath = path.join(__dirname, 'vite.config.js');
if (!fs.existsSync(viteConfigPath)) {
  problems.push('vite.config.js non trovato');
} else {
  console.log('   ✓ vite.config.js presente');
  try {
    const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');
    if (!viteConfig.includes('port')) {
      warnings.push('Porta non configurata in vite.config.js (verrà usata quella di default)');
    }
    if (viteConfig.includes('port: 5173')) {
      console.log('   ✓ Porta 5173 configurata');
    }
  } catch (error) {
    warnings.push(`Errore nella lettura di vite.config.js: ${error.message}`);
  }
}

// 5. Verifica index.html
console.log('\n5️⃣ Verifica file HTML...');
const indexHtmlPath = path.join(__dirname, 'index.html');
if (!fs.existsSync(indexHtmlPath)) {
  problems.push('index.html non trovato');
} else {
  console.log('   ✓ index.html presente');
  const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');
  if (!indexHtml.includes('root')) {
    problems.push('index.html non contiene elemento con id="root"');
  }
  if (!indexHtml.includes('main.jsx') && !indexHtml.includes('main.tsx')) {
    problems.push('index.html non contiene riferimento a main.jsx');
  }
}

// 6. Verifica sintassi file principali
console.log('\n6️⃣ Verifica sintassi file principali...');
const filesToCheck = [
  'src/main.jsx',
  'src/App.jsx'
];

for (const file of filesToCheck) {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      // Verifica base: controlla se è valido JSX
      if (content.includes('import') || content.includes('export')) {
        console.log(`   ✓ ${file} sembra valido`);
      }
    } catch (error) {
      warnings.push(`Errore nella lettura di ${file}: ${error.message}`);
    }
  } else {
    problems.push(`${file} non trovato`);
  }
}

// 7. Verifica variabili d'ambiente
console.log('\n7️⃣ Verifica configurazione ambiente...');
const envExamplePath = path.join(__dirname, '.env.example');
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envExamplePath)) {
  console.log('   ✓ .env.example presente');
}
if (!fs.existsSync(envPath)) {
  warnings.push('.env non trovato (potrebbe essere necessario per VITE_API_URL)');
} else {
  console.log('   ✓ .env presente');
}

// 8. Verifica porta disponibile (simulazione)
console.log('\n8️⃣ Informazioni porta...');
console.log('   ℹ️  Porta configurata: 5173');
console.log('   ℹ️  Verifica manuale: netstat -ano | findstr :5173');

// 9. Riepilogo
console.log('\n' + '='.repeat(60));
console.log('📊 RIEPILOGO');
console.log('='.repeat(60));

if (problems.length === 0 && warnings.length === 0) {
  console.log('\n✅ Nessun problema rilevato!');
  console.log('\n💡 Prova ad avviare con:');
  console.log('   npm run dev');
} else {
  if (problems.length > 0) {
    console.log('\n❌ PROBLEMI BLOCCANTI:');
    problems.forEach((p, i) => {
      console.log(`   ${i + 1}. ${p}`);
    });
  }
  
  if (warnings.length > 0) {
    console.log('\n⚠️  AVVISI:');
    warnings.forEach((w, i) => {
      console.log(`   ${i + 1}. ${w}`);
    });
  }
  
  console.log('\n💡 AZIONI CONSIGLIATE:');
  if (problems.some(p => p.includes('node_modules') || p.includes('Dipendenze'))) {
    console.log('   1. Esegui: npm install');
  }
  if (problems.some(p => p.includes('File mancanti'))) {
    console.log('   2. Verifica che tutti i file siano stati creati');
  }
  if (problems.length > 0) {
    console.log('   3. Risolvi i problemi sopra indicati');
  }
}

console.log('\n' + '='.repeat(60));
process.exit(problems.length > 0 ? 1 : 0);

