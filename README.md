<h3 align="center">Kumpulan Script Python Niko</h3>

## Tools

| Tool | Description |
|------|-------------|
| [saham_idx](saham_idx/) | Scraper data saham IDX → MySQL via SSH tunnel |

## Requirements

Install [uv](https://docs.astral.sh/uv/) (manages Python versions + dependencies):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Usage

Each tool is a self-contained uv project. Navigate into the tool directory, sync deps, set up `.env`, then run.

```bash
cd <tool_name>
cp .env.example .env       # fill in your credentials
uv sync                    # creates .venv and installs deps
uv run main.py
```

`uv sync` creates a local `.venv/` automatically — no manual venv activation needed.

## Contact

Nikolius - [@n1colius](https://twitter.com/n1colius) - n1colius.lau@gmail.com
