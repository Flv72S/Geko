-- Script SQL per creare il database Geko in PgAdmin
-- Eseguire questo script in PgAdmin dopo aver selezionato il database 'postgres'

-- Crea il database se non esiste
CREATE DATABASE geko_db;

-- Commento: Dopo aver creato il database, seleziona 'geko_db' e esegui:
-- Il file init.sql contiene le definizioni delle tabelle

-- Per verificare che il database sia stato creato:
-- SELECT datname FROM pg_database WHERE datname = 'geko_db';

