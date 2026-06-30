# ScrapTF2

<div align="center">

<img src="https://github.com/user-attachments/assets/47af9449-9afe-45e5-9459-c7b111681c7c" alt="ScrapTF2 Screenshot" width="800"/>

</div>

A tool for automated participation in raffles on [Scrap.TF](https://scrap.tf). The program scans active raffle pages, stores them in a local database, and enters them on your behalf.

## How it works

- Steam authentication via embedded browser (nodriver)
- Periodic scanning of `/raffles` and `/raffles/ending` pages
- Raffle data stored in a local SQLite database
- Automatic navigation to raffle pages and enter button interaction
- PyQt6 GUI with real-time stats and log output

## Tech stack

| Component | Description |
|-----------|-------------|
| **nodriver** | Undetected Chrome browser automation |
| **PyQt6** | Desktop UI with dark theme |
| **SQLite** | Local raffle storage (WAL mode) |
| **asyncio** | Async browser operations |

## Installation

### Pre-built EXE

1. Download `ScrapTF2.exe` from [releases](https://github.com/Lemirda/ScrapTF2/releases)
2. Place it in a separate folder
3. Run it and log in to Steam through the browser that opens

### From source

```bash
git clone https://github.com/Lemirda/ScrapTF2.git
cd ScrapTF2
pip install -r requirements.txt
python main.py
```

## Project structure

```
ScrapTF2/
├── main.py                 # Entry point
├── src/
│   ├── config.py           # Configuration
│   ├── browser/
│   │   ├── login.py        # Steam authentication
│   │   ├── scanner.py      # Scanning loop
│   │   └── scraper.py      # Page parsing & raffle entry
│   ├── db/
│   │   └── manager.py      # SQLite operations
│   └── ui/
│       ├── app.py          # Main PyQt6 window
│       ├── workers.py      # Background threads
│       └── styles.py       # Color scheme
├── scripts/
│   └── build.py            # PyInstaller build script
└── .github/
    └── workflows/
        └── build-release.yml  # CI/CD
```

## Security

- Browser profile stored locally in `browser_profile/`
- Credentials are not transmitted to any third party
- `raffles.db` database is created next to the executable
- Source code is open for review
