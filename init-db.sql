-- Script de inicialización de la base de datos PostgreSQL
-- Este archivo se ejecuta automáticamente cuando se crea el contenedor de PostgreSQL

-- Crear extensiones útiles (opcional)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- El resto de la inicialización se hace desde Django con las migraciones
SELECT 'Base de datos inicializada correctamente' as status;