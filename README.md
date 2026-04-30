<h3 align="center">Kumpulan Script Python Niko</h3>

## Tools

| Tool | Description |
|------|-------------|
| [saham_idx](saham_idx/) | Scraper data saham IDX → MySQL via SSH tunnel |

## Requirements (Ubuntu/Linux)

Make sure Python 3 and `pip` are installed:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Usage

Each tool is self-contained in its own folder. Navigate into the tool directory, install dependencies, set up `.env`, then run.

```bash
cd <tool_name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # fill in your credentials
python3 main.py
```

To deactivate the virtual environment when done:

```bash
deactivate
```

## Contact

Nikolius - [@n1colius](https://twitter.com/n1colius) - n1colius.lau@gmail.com
