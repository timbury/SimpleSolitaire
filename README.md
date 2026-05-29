# Simple Solitaire (Python + Kivy)
A basic, no-ads, no-in-app-purchases Klondike Solitaire game written in Python.

## What this includes
- Desktop app using Kivy (macOS, Linux, Windows)
- Core game logic separated from UI for easier future mobile work
- Simple click/tap interactions
- Unit tests for core rules

## Quick start
1. Create and activate a virtual environment.
2. Install dependencies.
3. Run the game.

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Desktop packaging (distribution builds)
PyInstaller builds are OS-specific, so run the build command on each target OS.

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
bash scripts/build_desktop.sh
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\build_desktop.ps1
```

Build outputs:
- macOS app bundle: `dist/SimpleSolitaire.app`
- Linux/Windows app folder: `dist/SimpleSolitaire`

## Controls
- **Stock**: draw next card (or recycle waste when stock is empty)
- **Waste**: click to select the top waste card
- **Tableau card**: click to select/move card stacks
- **Foundation pile**: click to move selected eligible card there
- **New Game**: shuffle and restart

## Project layout
- `main.py`: desktop app entry point
- `solitaire/engine.py`: Klondike game rules and state
- `solitaire/app.py`: Kivy UI
- `tests/test_engine.py`: unit tests

## Mobile plan (Android/iOS)
This codebase is structured so the `solitaire/engine.py` rules module can be reused as-is for mobile.

Later steps:
- Android: package with Buildozer
- iOS: package with kivy-ios
- Add touch polish and responsive layout tuning
