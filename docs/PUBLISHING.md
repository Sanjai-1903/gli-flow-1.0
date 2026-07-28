# Publishing gli-flow so students can `pip install gli-flow`

You now have a `pyproject.toml`, so the package builds into a proper wheel.
There are two ways students can install it. Pick based on how public you
want it.

## Option A — Install straight from GitHub (works right now, zero setup)

Students run:

```
pip install "git+https://github.com/Sanjai-1903/gli-flow-1.0.git"
```

That's it — no accounts, no publishing. The `gli-flow` command lands on
their PATH. They then:

```
gli-flow demo
gli-flow run gli-demo/counter --mock
export GLI_INGEST_URL='https://gli-flow-1-0-ingest.onrender.com'
export GLI_WEB_URL='https://<your-vercel-url>'
gli-flow login
```

This is the recommended path for the pilot. It's a slightly longer command
than `pip install gli-flow`, but nothing to maintain.

## Option B — Publish to PyPI so it's `pip install gli-flow` (public, ~20 min)

This makes the short command work, but the package name `gli-flow` must be
free on PyPI and the release is public to the world.

1. Make a PyPI account at https://pypi.org/account/register/ and create an
   API token (Account Settings → API tokens → scope: entire account).

2. Install build tooling (in your venv):
   ```
   pip install build twine
   ```

3. Build the wheel + sdist from the repo root:
   ```
   cd ~/Downloads/project_work/gli-flow-asic
   python3 -m build
   ```
   This writes `dist/gli_flow-1.1.0b0-py3-none-any.whl` and a `.tar.gz`.

4. Upload:
   ```
   python3 -m twine upload dist/*
   ```
   Username: `__token__`  Password: your PyPI API token (the whole
   `pypi-...` string).

5. If the name `gli-flow` is taken, change `name = "gli-flow"` in
   `pyproject.toml` to something free (e.g. `gli-flow-asic`,
   `gliflow-cli`) and rebuild. Students then install that name.

Once uploaded, anyone can:

```
pip install gli-flow
gli-flow demo
gli-flow run gli-demo/counter --mock
```

### Releasing updates

Bump `version` in `pyproject.toml` (e.g. `1.1.0b1`), rebuild, re-upload.
PyPI won't accept the same version twice.

### TestPyPI first (optional, safe rehearsal)

```
python3 -m twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ gli-flow
```

## What `gli-flow demo` does

Because a pip-installed package doesn't ship the repo's `examples/` folder,
`gli-flow demo` writes a self-contained counter design into
`./gli-demo/counter` (RTL + SDC + manifest). This guarantees students have
something to run regardless of how they installed the CLI.
