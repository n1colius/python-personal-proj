<h3 align="center">Kumpulan Script Python Niko</h3>

## Tools

| Tool | Description |
|------|-------------|
| [saham_idx](saham_idx/) | Scraper data saham IDX → MySQL via SSH tunnel |

## Usage

Each tool is self-contained in its own folder. Navigate into the tool directory, install dependencies, set up `.env`, then run.

```bash
cd <tool_name>
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # fill in your credentials
python main.py
```

## Contact

Nikolius - [@n1colius](https://twitter.com/n1colius) - n1colius.lau@gmail.com
