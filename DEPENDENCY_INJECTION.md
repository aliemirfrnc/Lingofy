# Dependency Injection Guide

## Principles
1. **No Global Singletons (Mostly):** Service and Repository lifetimes are bound to the FastAPI Request lifecycle. Do not use global module-level singletons for DB connections or services.
2. **Constructor Injection:** Services must receive their dependencies (Repositories, EventBus) via their constructors `__init__`. 
3. **FastAPI Depends:** The DI container logic resides in `backend/admin/dependencies.py` and is accessed in routes via `Depends()`.
