# Logging

PyScoundrel can log every game event to the console or a JSON Lines file for
later analysis.

## CLI flags

| Flag | Description |
|---|---|
| `--log-console` | Print events to stdout in human-readable format |
| `--log-file` | Write events to an auto-named `.jsonl` file in `logs/` |
| `--log-file path.jsonl` | Write events to a specific file |

```bash
# Console only
python -m pyscoundrel --log-console

# File only (auto-named)
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file

# Both
python -m pyscoundrel --agent examples/smart_agent.py --log-console --log-file
```

## Event types

| Event | When it fires |
|---|---|
| `game_start` | Game begins |
| `room_drawn` | 4 cards drawn into a room |
| `decision` | Player / agent makes a choice |
| `card_faced` | Weapon or potion resolved |
| `combat` | Monster fight resolved |
| `game_over` | Game ends (victory, death, or quit) |

## Log file format

Each line is a JSON object:

```
{
  "timestamp": "2026-02-09T21:47:27.984810",
  "event": "combat",
  "data": {
    "monster": "Goblin", "monster_value": 5,
    "method": "weapon",  "weapon": "Iron Sword", "weapon_value": 8,
    "damage": 0,         "health_after": 18
  },
  "state": { "player": { "health": 18, "max_health": 20, ... }, ... }
}
```

## Analysing logs with Python

```python
import json
from pathlib import Path

events = [json.loads(line) for line in Path("logs/game.jsonl").read_text().splitlines()]

# Final result
game_over = next(e for e in events if e["event"] == "game_over")
print(game_over["data"])   # {'victory': True, 'score': 12, ...}

# Total damage taken
total_damage = sum(
    e["data"].get("damage", 0) for e in events if e["event"] == "combat"
)

# Health trajectory
health = [e["state"]["player"]["health"] for e in events if e.get("state")]
```

## Programmatic usage

```python
from pyscoundrel.logging.logger import GameLogger

with GameLogger(log_to_console=True, log_file="game.jsonl") as logger:
    engine = GameEngine(logger=logger, seed=42)
    engine.start_game()
    ...
```
