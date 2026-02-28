# PyScoundrel

[![CI](https://github.com/jeanmidevacc/pyscoundrel/actions/workflows/ci.yml/badge.svg)](https://github.com/jeanmidevacc/pyscoundrel/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pyscoundrel)](https://pypi.org/project/pyscoundrel/)
[![Docs](https://readthedocs.org/projects/pyscoundrel/badge/?version=latest)](https://pyscoundrel.readthedocs.io/en/latest/)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://www.python.org)

A Python implementation of **Scoundrel**, a single-player roguelike card game by Zach Gage and Kurt Bieg.

## Installation

```bash
pip install pyscoundrel
```

## Play

```bash
python -m pyscoundrel

# With a fixed seed (reproducible game)
python -m pyscoundrel --seed 42

# Custom dungeon
python -m pyscoundrel --dungeon my_dungeon.yaml
```

## Features

- Complete Scoundrel rules — monsters, weapons, potions, room avoidance
- Clean terminal UI powered by [Rich](https://github.com/Textualize/rich)
- YAML-based dungeon system for custom card pools
- Agent API for automated players and strategy experiments
- JSON event logging for game analysis
- Random seed support for reproducible playthroughs

## Programmatic usage

```python
from pyscoundrel import GameEngine, Dungeon

engine = GameEngine(seed=42)
engine.start_game()

while not engine.is_game_over:
    engine.draw_room()
    result = engine.face_card(0)
    # inspect result.metadata to handle monsters, weapons, potions

print(f"Victory: {engine.state.victory} | Score: {engine.state.score}")
```

## Documentation

Full documentation at **[pyscoundrel.readthedocs.io](https://pyscoundrel.readthedocs.io)**:

- [Quick Start](https://pyscoundrel.readthedocs.io/en/latest/guides/quickstart.html)
- [Dungeon Configuration](https://pyscoundrel.readthedocs.io/en/latest/guides/dungeon.html)
- [Logging](https://pyscoundrel.readthedocs.io/en/latest/guides/logging.html)
- [API Reference](https://pyscoundrel.readthedocs.io/en/latest/api/index.html)

## License

MIT. The original Scoundrel game is © 2011 Zach Gage and Kurt Bieg.
