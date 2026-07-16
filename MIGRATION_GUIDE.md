# Migration Guide

## Rules
1. **No ALTER/DROP:** Only `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` are permitted for existing live environments to guarantee Zero Regression.
2. **Isolation:** Admin schemas are managed separately inside `backend/admin/migrations/`. Do not pollute the core app migrations.
3. **Rollback capability:** Ensure `downgrade` drops the newly created tables exclusively, without dropping shared tables from core.
4. **Idempotency:** A migration run multiple times must not crash.

## Executing Migrations
Admin migrations execute automatically via `initialize_admin_schema()` during app startup or testing fixture initialization.
