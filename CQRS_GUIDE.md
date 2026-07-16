# CQRS Guide

## Repository Layer
Operations Backend utilizes a strict CQRS (Command Query Responsibility Segregation) pattern for Database Access at the repository level. 
Repositories only handle data persistence and retrieval: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
Validation, permissions, transaction logic, and business logic are banned from the Repository layer.

## Guidelines
1. **Separation**: Read Repositories only fetch data. Write Repositories mutate data.
2. **Cursor Pagination**: Use cursor-based offsets `WHERE id < ? ORDER BY id DESC LIMIT ?`. Do NOT use `OFFSET`.
3. **Batch Inserts**: Use `executemany` for high-volume logs (e.g. Telemetry, Metrics) to reduce Database overhead.
