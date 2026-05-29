# Simple Solitaire (Python + Kivy)
A simple, no-ads, no-in-app-purchases Klondike Solitaire game.

## Requirements
- Python 3.10+
- `pip`

## 1) Set up the project
### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Run the game (development mode)
```bash
python main.py
```

## 3) Artwork assets (optional but recommended)
The app supports image-based rendering for card backs/faces and table background.

Place artwork under:
- `assets/cards/fronts/` for face cards (`AS.png`, `2S.png`, ... `KH.png`)
- `assets/cards/backs/` for card back image (`card_back.png` preferred)
- `assets/ui/` for table background (`table_felt.png` preferred)

If an image is missing, the app falls back to text rendering for that element.

## 4) Run tests
```bash
PYTHONPATH=. python -m unittest discover -s tests
```

## 5) Build desktop distribution
PyInstaller builds are OS-specific. Build on each target OS.

### macOS / Linux
```bash
bash scripts/build_desktop.sh
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_desktop.ps1
```

The build scripts bundle the `assets/` directory into the packaged app.

## 6) Run packaged app
- macOS: `dist/SimpleSolitaire.app` (or binary at `dist/SimpleSolitaire.app/Contents/MacOS/SimpleSolitaire`)
- Linux/Windows: executable inside `dist/SimpleSolitaire/`

## Controls
- **Stock**: draw next card (or recycle waste when stock is empty)
- **Waste**: select the top waste card
- **Tableau card**: select/move card stacks
- **Foundation pile**: move selected eligible card there
- **New Game**: reshuffle and restart
