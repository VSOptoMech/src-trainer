# src-trainer

Minimal local-first Python web app scaffold for personal SRC (marine VHF radio) training, built with NiceGUI.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Install uv

Use Astral's install guide: <https://docs.astral.sh/uv/getting-started/installation/>.

Quick install examples:

- macOS / Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Windows (PowerShell):

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

## Run from this repository

From the repo root:

```bash
uv run src-trainer
```

The app opens at `http://127.0.0.1:8080`.

## Run directly from GitHub with uvx

```bash
uvx --from git+https://github.com/OWNER/REPO src-trainer
```

Replace `OWNER/REPO` with the real repository path.

## Local database location

`src-trainer` stores progress in a per-user writable SQLite file:

- Linux: `$XDG_DATA_HOME/src-trainer/src_trainer.db` (or `~/.local/share/src-trainer/src_trainer.db`)
- macOS: `~/Library/Application Support/src-trainer/src_trainer.db`
- Windows: `%LOCALAPPDATA%\src-trainer\src_trainer.db`

When the app starts, it prints the exact database path being used.

## Reset progress

Delete the local database file shown at startup, then run `src-trainer` again.

Example (Linux default path):

```bash
rm ~/.local/share/src-trainer/src_trainer.db
```

## If port 8080 is busy

If another app is already using `127.0.0.1:8080`, `src-trainer` exits cleanly and prints a clear message.
Close the conflicting app, then run again.
