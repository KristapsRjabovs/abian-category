# abian-category

B2B unified category tree editor. One Postgres database (Neon, hosted on
Netlify) is the source of truth. Flask serves the editor locally; Netlify
hosts the same UI with serverless functions that talk to Postgres directly.

## Layout

    app.py              Flask server (UI + Magento export endpoint)
    db.py               Postgres layer + connection pool
    build.py            Bakes initial editor state into public/index.html
    migrate.py          Applies pending migrations from migrations/
    migrations/         Numbered schema/data migrations (NNN_name.py)
    test_roundtrip.py   Save/load integration test (Python, hits app.py)
    test_netlify_live.py  Smoke test against a deployed Netlify environment

    templates/          Jinja templates rendered by Flask + bake target
    raw/                Source supplier-category CSVs (read-only inputs)
    netlify/            Serverless functions (read/write Postgres via @netlify/neon)

## Local development

You need a Postgres URL. Cheapest option: copy the Neon URL from the
Netlify dashboard (Site → Extensions → Neon → Environment variables) and
drop it into `.env`:

    cp .env.example .env
    # paste DATABASE_URL=postgres://...

Then:

    pip install -r requirements.txt
    python3 migrate.py     # apply any pending migrations against Neon
    python3 app.py         # http://localhost:5000

If you want a fully isolated local Postgres (no risk to live data) install
`pgserver` and point `DATABASE_URL` at the embedded instance:

    pip install pgserver
    python3 -c "import pgserver, os; pg = pgserver.get_server('/tmp/pg_abian'); print(pg.get_uri())"
    # paste that URL into .env, then run migrate + app

## Tests

    python3 test_roundtrip.py                              # against app.py
    NETLIFY_URL=https://<site> python3 test_netlify_live.py  # against deployed JS

## Deploy

Netlify build runs `pip install -r requirements.txt && python3 migrate.py
&& python3 build.py`. New migrations are applied on every deploy; the build
then bakes the initial editor state into `public/index.html`.

## Migrations

Anything that changes schema or seeds data goes through a new migration
file. Naming: `migrations/NNN_short_description.py` exposing `apply(conn)`.
The runner records each applied filename in `_migrations` so it never runs
twice. Use `python3 migrate.py --status` to see pending ones.

To pull live edits back into the committed history, write a new migration
that updates Postgres directly. The previous Blobs-based snapshot path is
gone — Postgres is shared between Netlify and your laptop.

## Backup / restore

Neon takes automatic point-in-time backups; the dashboard has a one-click
restore. For a manual export:

    pg_dump "$DATABASE_URL" > backups/abian-$(date +%F).sql

Restore into a fresh database:

    psql "$NEW_DATABASE_URL" < backups/abian-2026-04-26.sql

## Migration cleanup

Migration `003_import_live_blobs.py` and its `_live_snapshot.json` exist
solely to seed Postgres on the first deploy. Once that has run on every
environment (production, staging, local), both can be deleted in a follow-up
commit — the data lives in Postgres now, not in the snapshot file.

## Things deleted on purpose

These used to exist; everything they stored is now in Postgres:

  * `state.json`, `seo_content/*.xml`  -> tree_nodes / mappings / tree_state
  * `build_categories.py`              -> tree_nodes
  * `seo.py`, `migrate_seo.py`,
    `seo_xml.py`, `seed.py`            -> migrations
  * `category.db` (SQLite)             -> Neon Postgres
  * Netlify Blobs (`@netlify/blobs`)   -> Neon Postgres
  * `netlify/functions/_data.json`     -> functions read DB directly
  * `netlify/functions/reset-seo.mjs`,
    `sync-state-json.mjs`              -> no Blobs to sync
