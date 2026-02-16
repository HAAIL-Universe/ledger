"""Services layer — business logic orchestration for Ledger.

This package contains service modules that coordinate workflows between
repositories, clients, and processors. Services implement the core business
rules for receipt processing, expense extraction, and user management.

Services MUST NOT:
- Import FastAPI request/response types
- Execute raw SQL or access the database directly
- Make direct external API calls (use clients instead)

Services SHOULD:
- Orchestrate multi-step operations (e.g., upload → OCR → store)
- Delegate data access to repos
- Delegate external API calls to clients
- Contain business validation and workflow logic
"""
