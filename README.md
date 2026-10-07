# Runway Rush — Python + Pygame

A standalone **3-lane endless runner** made with Python and Pygame.

This is an original mini-game inspired by the endless-runner genre. It does not use Subway Surfers assets, characters, or code.

## Features

- 3-lane runner
- Lane switching
- Jump
- Slide
- Coins
- Barriers and crates
- Increasing speed
- Score and best score
- Pause/resume
- Game over and restart
- Keyboard controls
- Local JSON save
- No backend
- No database
- No API

## Requirements

- Python 3.10+
- Pygame 2.6+

## Install

Open a terminal in this project folder:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

| Key | Action |
|---|---|
| Left / A | Move left |
| Right / D | Move right |
| Up / W / Space | Jump |
| Down / S | Slide |
| P / Esc | Pause / Resume |

## Save data

The game automatically creates:

```text
runway_rush_save.json
```

It stores:

- Best score
- Total coins
- Number of games
- Sound preference

Everything is local to the computer. Nothing is uploaded to a server.

## Project structure

```text
runway-rush-pygame/
├── main.py
├── requirements.txt
└── README.md
```

## Build an executable

You can optionally package it later with PyInstaller:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The executable will be placed inside the `dist` directory.

## Future upgrades

The project is intentionally backend-free. Later you can add:

- Player profiles
- Online leaderboard
- Cloud save
- Skins
- Missions
- Achievements
- Daily challenges
- More obstacle types
- Character animation
- Sprite sheets
- Music
- Particle effects
- Multiple maps

## License

Use and modify this project for learning and personal projects. Add your own license before distributing it publicly.
