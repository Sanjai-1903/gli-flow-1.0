# GLI Flow — Student Quickstart

You do **not** need to clone the repo, and you do **not** need Linux or WSL.
The CLI is pure Python and runs on Windows, macOS, and Linux. You only need
**Python 3.9+** installed.

Check you have Python:

```
python --version
```

If that fails, install Python from https://www.python.org/downloads/ (on
Windows, tick **"Add Python to PATH"** during install).

---

## 1. Install the CLI (one command)

You have two options. Both give you the `gli-flow` command.

### Option A — install the wheel file (simplest, no build)

Download `gli_flow-1.1.0b0-py3-none-any.whl` (your instructor shares it, or
grab it from the GitHub Releases page), then:

**Windows (PowerShell):**
```
py -m pip install gli_flow-1.1.0b0-py3-none-any.whl
```

**macOS / Linux:**
```
python3 -m pip install gli_flow-1.1.0b0-py3-none-any.whl
```

### Option B — install straight from GitHub

**Windows (PowerShell):**
```
py -m pip install "git+https://github.com/Sanjai-1903/gli-flow-1.0.git"
```

**macOS / Linux:**
```
python3 -m pip install "git+https://github.com/Sanjai-1903/gli-flow-1.0.git"
```

> Tip: if `pip` complains about permissions, add `--user`:
> `py -m pip install --user <same thing>`

You do **not** need to create a virtual environment. If you want one anyway,
note the activation command differs by OS:
> - Windows PowerShell: `python -m venv .venv ; .venv\Scripts\Activate.ps1`
> - macOS / Linux:       `python3 -m venv .venv && source .venv/bin/activate`
>
> (This is the step that trips people up — `source .venv/bin/activate` is
> macOS/Linux only. On Windows use `.venv\Scripts\Activate.ps1`.)

Confirm it installed:

```
gli-flow --help
```

If `gli-flow` isn't found on Windows, use `py -m gli_flow` instead, or close
and reopen your terminal so PATH refreshes.

---

## 2. Connect the CLI to your account

First, point it at the server (do this once per terminal — or add it to your
shell profile so it sticks):

**Windows (PowerShell):**
```
$env:GLI_INGEST_URL = "https://gli-flow-1-0-ingest.onrender.com"
$env:GLI_WEB_URL     = "https://<your-production-vercel-url>"
```

**macOS / Linux:**
```
export GLI_INGEST_URL='https://gli-flow-1-0-ingest.onrender.com'
export GLI_WEB_URL='https://<your-production-vercel-url>'
```

Then log in. Two ways:

**Easiest — browser login:**
```
gli-flow login
```
This prints a code and opens your browser. Sign in with Google, confirm the
code, done.

**Or — paste a token:** on the website, open **CLI Tokens → New token**, copy
it, then:
```
gli-flow login --token gfp_your_token_here
```

Confirm it worked (should print your email):
```
gli-flow whoami
```

---

## 3. Run a design

```
gli-flow demo
gli-flow run gli-demo/counter --mock
```

`--mock` runs a simulated flow (no heavy EDA tools needed) so you can test the
whole pipeline in under a minute. When it finishes, it auto-uploads to your
account — refresh the website and your run appears.

---

## Troubleshooting

- **`source: no such file` on Windows** — that command is macOS/Linux only.
  You don't need a venv at all; just `pip install` and run `gli-flow`.
- **`gli-flow: command not found`** — reopen your terminal, or run it as
  `py -m gli_flow` (Windows) / `python3 -m gli_flow` (Mac/Linux).
- **`git` errors while installing** — use Option A (the wheel file) instead;
  it needs no git.
- **Login says it can't reach the server** — the server may be waking up
  (first request after idle takes ~30s). Wait and retry `gli-flow login`.
```
