-- ============================================================
-- Script SQL per creare il database Geko in PgAdmin
-- ============================================================
-- 
-- ISTRUZIONI:
-- 1. Apri PgAdmin 4
-- 2. Connettiti al server PostgreSQL (usa le tue credenziali)
-- 3. Seleziona il database "postgres" (database di default)
-- 4. Apri Query Tool (icona SQL o clic destro)
-- 5. Incolla questo script
-- 6. Esegui (F5 o pulsante Execute)
--
-- ============================================================

-- Crea il database se non esiste
-- Nota: Se il database esiste già, questo comando fallirà con un errore
--       che puoi ignorare se vuoi mantenere i dati esistenti
CREATE DATABASE geko_db;

-- ============================================================
-- Dopo aver creato il database:
-- ============================================================
-- 1. Seleziona il database "geko_db" nel pannello sinistro
-- 2. Apri Query Tool
-- 3. Esegui il file backend/init.sql per creare le tabelle
--    oppure incolla il contenuto di init.sql

-- ============================================================
-- Verifica che il database sia stato creato:
-- ============================================================
SELECT datname, datcollate, datctype 
FROM pg_database 
WHERE datname = 'geko_db';

