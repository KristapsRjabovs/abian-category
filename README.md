# abian-category

B2B unified category tree editor. Single SQLite database is the source of
truth; Flask serves the editor locally; Netlify hosts the same UI with
serverless functions reading the baked build artifacts plus a Blobs delta.

## Layout

    app.py              Flask server (UI + APIs)
    db.py               SQLite layer
    build.py            Bakes category.db -> public/index.html + _data.json
    migrate.py          Applies pending migrations from migrations/
    migrations/         Numbered schema/data migrations (NNN_name.py)
    test_roundtrip.py   Save/load integration test
    category.db         The data. Committed.

    templates/          Jinja templates rendered by Flask + bake target
    raw/                Source supplier-category CSVs (read-only inputs)
    netlify/            Serverless functions and netlify.toml

## Local dev

    pip install -r requirements.txt
    python3 migrate.py        # apply any new schema/data migrations
    python3 app.py            # http://localhost:5000

## Tests

    python3 test_roundtrip.py

## Deploy

Netlify build runs `pip install -r requirements.txt && python3 migrate.py
&& python3 build.py`. The committed `category.db` is the source of truth;
migrations only add schema/data on top.

## Sync live edits back to git

When you have edited the tree on the hosted site and want those edits to
land in the committed DB:

    curl https://<site>/api/sync-state-json > /tmp/live.json
    # then write a migrations/NNN_pull_<date>.py that applies that JSON
    # to the local DB, commit category.db + the migration, push.

## Things deleted on purpose

These used to exist; everything they stored is now in `category.db`:

  * `state.json`, `seo_content/*.xml`  -> tree_nodes / mappings / tree_state
  * `build_categories.py`              -> tree_nodes
  * `seo.py`, `migrate_seo.py`,
    `seo_xml.py`, `seed.py`            -> migrations
