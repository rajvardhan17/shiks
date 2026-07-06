# Known Issues Fixed During Migration

## 1. Fabricated fallback data
- Problem: The old aggregator used hardcoded defaults for missing scraped fields, such as `₹ 6.5 LPA`, `80%`, `2001`, `NAAC A`, and fake course names.
- Fix: All missing values now remain `None`, empty lists, or empty dicts. A `data_completeness` metadata block is added to every payload so incomplete records are visible.

## 2. Established year false positives
- Problem: The old code accepted any bare 4-digit year between 1800 and 2026, which produced false positives from copyright notices and admission banners.
- Fix: The new parser only accepts years adjacent to keywords like `estd`, `established`, `founded`, `est.`, or `since`, and rejects years within the last 2 years.

## 3. Missing SessionLocal
- Problem: The original `db/session.py` exposed only `get_session_factory()` and did not define `SessionLocal`, causing `SessionLocal()` call sites to fail.
- Fix: `edusphere/db/session.py` now exports a module-level singleton `SessionLocal = get_session_factory()`.

## 4. Field-name collision with internal links
- Problem: `internal_links` keys like `admissions` and `placements` collided with structured data columns during export.
- Fix: `internal_links` is now stored separately, and exports flatten nested links as `internal_link_admissions`, `internal_link_placements`, etc.

## 5. Two parallel savers
- Problem: The repo contained both `saver.py` and `saver_postgres.py`, suggesting an incomplete dual persistence design.
- Fix: The migration consolidates persistence into a single `edusphere/pipelines/storage_pipeline.py` that writes to Postgres via SQLAlchemy.
