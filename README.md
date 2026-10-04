# Domain Copilot — Healthcare (D0) + Document In/Out (T6)

Agentic RAG platform for clinical evidence and documentation.

## Variant derivation
- National ID last two digits = 42 → 42 mod 7 = 0 → **D0 Healthcare**
- Sum of all digits = 30 → 30 mod 8 = 6 → **T6 Document in/out**

## Starter/template declaration
No starter or template used. Built from scratch.

## Status
Work in progress. Full docs coming.

## Quick start
1. `cp .env.example .env`
2. `docker compose up --build`
3. Open http://localhost:8000/health