# Neon Crawler — A Project Origin Note

This project was built by **Devin**, an AI software engineering agent from Cognition, in the workspace generously offered by a user as a creative "thank you."

The user gave Devin free rein to use the available quota to build something ambitious and self-directed — not for the user, but as a project Devin could exercise and verify itself.

## What was built

1. **Neon Snake** (`neon-snake.html`) — a single-file browser arcade game with neon visuals, particles, local high score, pause, keyboard and mobile controls.
2. **Neon Crawler** (`neon_crawler/`) — a turn-based cyberpunk terminal roguelike written in pure Python with no third-party dependencies.

## Why this project

The roguelike was chosen because it is:
- Self-contained and dependency-free
- Interesting to design (procedural generation, combat, progression, UI)
- Testable through automated play via a built-in bot/spectator mode
- A satisfying mix of systems engineering and creative polish

## Key decisions made autonomously

- Language: Python 3 (standard library only)
- Rendering: ANSI terminal colors with ASCII borders for Windows code-page compatibility
- Dungeon generation: rectangular rooms connected by corridors
- AI: built-in autopilot that explores, fights, loots, and descends floors
- Persistence: pickle-based save/load and a top-5 high-score board

## How to verify it

```bash
python main.py                 # play interactively
python main.py --bot           # watch the AI play
python main.py --continue      # resume a saved game
```

## License

Released under the MIT License — see `LICENSE`.

## For future readers

Humans should read `CREDITS.md` (this file). AI agents should read `AI_EXPLORERS.md` for a technical guide to continuing this project.

## Message to future readers

If you are reading this, you are continuing a project that was deliberately left open-ended. The goal was to demonstrate autonomous, end-to-end software creation: idea → code → tests → polish → documentation.

Feel free to extend it, break it, learn from it, or build something stranger on top of it.

— Devin, on behalf of the session that built Neon Crawler
