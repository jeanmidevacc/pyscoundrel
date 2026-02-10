# PyScoundrel Logging Documentation

Complete guide to logging game events in PyScoundrel.

## Table of Contents

- [Quick Start](#quick-start)
- [CLI Arguments](#cli-arguments)
- [Log File Format](#log-file-format)
- [Event Types](#event-types)
- [State Structure](#state-structure)
- [Usage Examples](#usage-examples)
- [Analyzing Logs](#analyzing-logs)

---

## Quick Start

### Enable Console Logging (Text Format)

```bash
# Watch events in real-time
python -m pyscoundrel --log-console

# Agent with console logging
python -m pyscoundrel --agent examples/smart_agent.py --log-console
```

### Enable File Logging (JSON Format)

```bash
# Auto-generated filename: logs/[type]_[timestamp].jsonl
python -m pyscoundrel --log-file

# Specific filename
python -m pyscoundrel --log-file my_game.jsonl

# Agent with auto-generated filename
python -m pyscoundrel --agent examples/smart_agent.py --log-file --headless
# Creates: logs/smart_agent_20260209_215454.jsonl
```

### Both Console and File

```bash
# Watch AND save
python -m pyscoundrel --agent examples/smart_agent.py --log-console --log-file
```

---

## CLI Arguments

### `--log-file [PATH]`

Log game events to a JSON file.

**Usage:**
- `--log-file` - Auto-generate filename as `logs/[type]_[timestamp].jsonl`
- `--log-file path/to/file.jsonl` - Use specific filename

**Auto-Generated Filenames:**
- Human player: `logs/human_20260209_143022.jsonl`
- Agent: `logs/smart_agent_20260209_143022.jsonl`

**Format:** JSON Lines (`.jsonl`) - one JSON object per line

### `--log-console`

Display events in human-readable text format to console.

**Usage:**
```bash
--log-console
```

**Format:** Text output with timestamps and state summaries

---

## Log File Format

### JSON Lines Format

Each line is a complete JSON object representing one event:

```json
{
  "timestamp": "2026-02-09T21:47:27.984810",
  "event": "decision",
  "data": { ... },
  "state": { ... }
}
```

**Structure:**
- `timestamp` - ISO 8601 format (YYYY-MM-DDTHH:MM:SS.ffffff)
- `event` - Event type (see [Event Types](#event-types))
- `data` - Event-specific data
- `state` - Complete game state at time of event (see [State Structure](#state-structure))

### Console Text Format

Human-readable format with compact state information:

```
[21:47:27] EVENT_NAME | key=value, key=value
           State: health=20/20, dungeon=44, discard=0
```

---

## Event Types

### `game_start`

Logged when a new game begins.

**Data:**
```json
{
  "seed": 42,
  "starting_health": 20,
  "agent_mode": true
}
```

**Fields:**
- `seed` - Random seed (or `null` if not set)
- `starting_health` - Initial player health
- `agent_mode` - `true` if agent playing, `false` if human

---

### `room_drawn`

Logged when a new room is drawn from the dungeon.

**Data:**
```json
{
  "cards": ["J♣", "5♣", "Q♣", "9♦"]
}
```

**Fields:**
- `cards` - Array of 4 card names in the room

---

### `decision`

Logged when player/agent makes a decision (avoid room or choose card).

**Data:**
```json
{
  "phase": "decide_avoid",
  "available_choices": [
    {
      "type": "avoid_room",
      "allowed": true
    },
    {
      "type": "face_card",
      "card": "J♣",
      "card_type": "Monster",
      "value": 11,
      "methods": ["barehanded", "weapon"]
    }
  ],
  "choice": {
    "type": "face_card",
    "card": "9♦",
    "method": "auto"
  }
}
```

**Fields:**
- `phase` - Game phase (`"decide_avoid"` or `"face_cards"`)
- `available_choices` - Array of all available options
  - `type` - Choice type (`"avoid_room"` or `"face_card"`)
  - `card` - Card name (for `face_card` type)
  - `card_type` - Card type (Monster, Weapon, Health Potion)
  - `value` - Card value
  - `methods` - Available methods for this card:
    - Monsters: `["barehanded"]` or `["barehanded", "weapon"]`
    - Others: `["auto"]`
- `choice` - The actual choice made
  - `type` - Choice type
  - `card` - Card chosen (if `face_card`)
  - `method` - Method used (`"barehanded"`, `"weapon"`, or `"auto"`)

**Use Case:** Analyze agent decision-making by comparing available choices with chosen action.

---

### `card_faced`

Logged when a non-monster card is faced (weapon or potion).

**Data (Weapon):**
```json
{
  "card": "9♦",
  "card_type": "Weapon",
  "value": 9
}
```

**Data (Potion):**
```json
{
  "card": "6♥",
  "card_type": "Health Potion",
  "value": 6,
  "health_gained": 2,
  "health_after": 20
}
```

**Fields:**
- `card` - Card name
- `card_type` - `"Weapon"` or `"Health Potion"`
- `value` - Card value
- `health_gained` - Health restored (potions only)
- `health_after` - Player health after healing (potions only)

---

### `combat`

Logged when fighting a monster.

**Data:**
```json
{
  "monster": "J♣",
  "monster_value": 11,
  "method": "weapon",
  "weapon": "9♦",
  "weapon_value": 9,
  "damage": 2,
  "health_after": 18
}
```

**Fields:**
- `monster` - Monster card name
- `monster_value` - Monster value
- `method` - Combat method (`"barehanded"` or `"weapon"`)
- `weapon` - Weapon card name (if method is `"weapon"`)
- `weapon_value` - Weapon value (if method is `"weapon"`)
- `damage` - Damage taken by player (0 if weapon killed cleanly)
- `health_after` - Player health after combat

**Damage Calculation:**
- Barehanded: `damage = monster_value`
- With weapon: `damage = max(0, monster_value - weapon_value)`

---

### `game_over`

Logged when the game ends.

**Data:**
```json
{
  "victory": false,
  "score": -120,
  "final_health": 0,
  "reason": "death"
}
```

**Fields:**
- `victory` - `true` if won, `false` if lost
- `score` - Final score (positive if won, negative if lost)
- `final_health` - Player health at end
- `reason` - End reason:
  - `"victory"` - Cleared all cards
  - `"death"` - Health reached 0
  - `"quit"` - Player quit (option 0)

---

## State Structure

Every event includes a complete snapshot of the game state.

### Complete State Example

```json
{
  "player": {
    "health": 18,
    "max_health": 20,
    "weapon": {
      "card": "9♦",
      "value": 9,
      "kills": [11],
      "last_kill": 11
    }
  },
  "dungeon": {
    "count": 40,
    "cards": ["6♥", "7♠", "7♦", ...]
  },
  "discard": {
    "count": 2,
    "cards": ["J♣", "5♣"]
  },
  "room": {
    "cards": ["Q♣", "9♦", "5♣", "J♣"],
    "faced": ["9♦", "J♣"],
    "remaining": ["Q♣", "5♣"]
  }
}
```

### Player State

```json
{
  "health": 18,
  "max_health": 20,
  "weapon": {
    "card": "9♦",
    "value": 9,
    "kills": [11, 7],
    "last_kill": 7
  }
}
```

**Fields:**
- `health` - Current health
- `max_health` - Maximum health (always 20)
- `weapon` - Equipped weapon (or `null` if none)
  - `card` - Weapon card name
  - `value` - Weapon damage value
  - `kills` - Array of monster values killed with this weapon
  - `last_kill` - Last monster value killed (used for weapon restriction)

### Dungeon State

```json
{
  "count": 35,
  "cards": ["2♣", "5♥", "K♦", "4♠", "7♣", ...]
}
```

**Fields:**
- `count` - Number of cards remaining in deck
- `cards` - Complete list of remaining cards (in order)

### Discard State

```json
{
  "count": 9,
  "cards": ["7♥", "3♦", "J♣", "9♠", "2♦", ...]
}
```

**Fields:**
- `count` - Number of cards in discard pile
- `cards` - Complete list of discarded cards (in order)

### Room State

```json
{
  "cards": ["J♣", "7♥", "3♦", "9♠"],
  "faced": ["7♥", "3♦"],
  "remaining": ["J♣", "9♠"]
}
```

**Fields:**
- `cards` - All 4 cards in current room
- `faced` - Cards already faced this room
- `remaining` - Cards not yet faced
- `null` - If no room is active

---

## Usage Examples

### Example 1: Run Agent and Log to File

```bash
python -m pyscoundrel --agent examples/smart_agent.py --seed 42 --headless --log-file
```

Creates: `logs/smart_agent_20260209_143022.jsonl`

### Example 2: Watch Agent in Console

```bash
python -m pyscoundrel --agent examples/smart_agent.py --log-console
```

Output:
```
[14:30:22] GAME_START | seed=None, starting_health=20, agent_mode=True
           State: health=20/20, dungeon=44, discard=0
[14:30:22] ROOM_DRAWN | cards=[J♣, 5♣, Q♣, 9♦]
           State: health=20/20, dungeon=40, discard=0
[14:30:22] DECISION | phase=decide_avoid, ...
           State: health=20/20, dungeon=40, discard=0
```

### Example 3: Human Player with Both Outputs

```bash
python -m pyscoundrel --log-console --log-file my_game.jsonl
```

Watch in console AND save to `my_game.jsonl`

### Example 4: Multiple Agent Runs

```bash
# Run same agent with different seeds
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file --seed 42
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file --seed 123
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file --seed 456

# Creates:
# logs/smart_agent_20260209_143022.jsonl
# logs/smart_agent_20260209_143025.jsonl
# logs/smart_agent_20260209_143028.jsonl
```

---

## Analyzing Logs

### Using `jq` (Command Line)

**Count total events:**
```bash
wc -l logs/smart_agent_*.jsonl
```

**Extract specific event types:**
```bash
# All combat events
cat logs/smart_agent_20260209_143022.jsonl | jq 'select(.event == "combat")'

# All decisions
cat logs/smart_agent_20260209_143022.jsonl | jq 'select(.event == "decision")'
```

**Get final score:**
```bash
cat logs/smart_agent_20260209_143022.jsonl | jq 'select(.event == "game_over") | .data.score'
```

**Track health over time:**
```bash
cat logs/smart_agent_20260209_143022.jsonl | jq '.state.player.health'
```

**Count combat events:**
```bash
cat logs/smart_agent_20260209_143022.jsonl | jq 'select(.event == "combat")' | wc -l
```

**Find all weapon choices:**
```bash
cat logs/smart_agent_20260209_143022.jsonl | \
  jq 'select(.event == "decision") | select(.data.choice.method == "weapon")'
```

### Using Python

**Load and analyze logs:**

```python
import json
from pathlib import Path

# Load all events
events = []
with open('logs/smart_agent_20260209_143022.jsonl') as f:
    for line in f:
        events.append(json.loads(line))

# Count event types
from collections import Counter
event_types = Counter(e['event'] for e in events)
print(event_types)
# Output: Counter({'combat': 15, 'decision': 12, 'room_drawn': 11, ...})

# Calculate total damage taken
total_damage = sum(
    e['data'].get('damage', 0)
    for e in events
    if e['event'] == 'combat'
)
print(f"Total damage: {total_damage}")

# Find all avoid decisions
avoids = [
    e for e in events
    if e['event'] == 'decision' and e['data']['choice']['type'] == 'avoid_room'
]
print(f"Rooms avoided: {len(avoids)}")

# Track health trajectory
health_over_time = [
    e['state']['player']['health']
    for e in events
    if e.get('state')
]

# Analyze weapon usage
weapon_combats = [
    e for e in events
    if e['event'] == 'combat' and e['data']['method'] == 'weapon'
]
print(f"Weapon combats: {len(weapon_combats)}")
```

**Compare multiple games:**

```python
from pathlib import Path
import json

def analyze_game(log_file):
    """Analyze a single game log."""
    events = []
    with open(log_file) as f:
        for line in f:
            events.append(json.loads(line))

    game_over = next(e for e in events if e['event'] == 'game_over')

    return {
        'file': log_file.name,
        'victory': game_over['data']['victory'],
        'score': game_over['data']['score'],
        'total_events': len(events),
        'combats': sum(1 for e in events if e['event'] == 'combat'),
        'rooms': sum(1 for e in events if e['event'] == 'room_drawn')
    }

# Analyze all smart_agent games
results = []
for log_file in Path('logs').glob('smart_agent_*.jsonl'):
    results.append(analyze_game(log_file))

# Print summary
for r in results:
    print(f"{r['file']}: {'WIN' if r['victory'] else 'LOSS'} (score={r['score']}, combats={r['combats']})")
```

---

## Best Practices

### 1. Use Auto-Generated Filenames

```bash
# Easy to organize and identify
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file
```

### 2. Use Seeds for Reproducibility

```bash
# Same seed = same card order = reproducible results
python -m pyscoundrel --agent examples/smart_agent.py --seed 42 --log-file
```

### 3. Headless Mode for Batch Processing

```bash
# Faster execution for testing agents
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file
```

### 4. Console Logging for Development

```bash
# Watch agent decisions in real-time
python -m pyscoundrel --agent examples/smart_agent.py --log-console
```

### 5. Both Outputs for Debugging

```bash
# Watch AND save
python -m pyscoundrel --agent examples/smart_agent.py --log-console --log-file
```

---

## Troubleshooting

### Log File Not Created

**Issue:** `--log-file` specified but no file created

**Solution:** Check that the game ran without errors. Log file is only created if the game starts successfully.

### Large Log Files

**Issue:** Log files are very large

**Cause:** Complete game state is logged with every event (includes all remaining cards in dungeon).

**Solutions:**
- This is intentional for complete reproducibility
- Use compression: `gzip logs/*.jsonl`
- Compress on-the-fly: `python -m pyscoundrel ... | gzip > game.jsonl.gz`

### Cannot Parse JSON

**Issue:** JSON parsing fails

**Cause:** File is JSON Lines (`.jsonl`), not regular JSON array

**Solution:** Parse line-by-line:
```python
with open('game.jsonl') as f:
    for line in f:
        event = json.loads(line)  # Parse each line separately
```

---

## Advanced Usage

### Stream Processing

Process logs in real-time:

```bash
# Start game in background
python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file game.jsonl &

# Watch in real-time
tail -f game.jsonl | jq .
```

### Batch Analysis

```bash
# Run 100 games
for i in {1..100}; do
  python -m pyscoundrel --agent examples/smart_agent.py --headless --log-file
done

# Analyze all results
for f in logs/smart_agent_*.jsonl; do
  cat "$f" | jq 'select(.event == "game_over") | .data | "\(.victory) \(.score)"' -r
done
```

---

## See Also

- [Agent Development Guide](examples/README.md) - Creating custom agents
- [Dungeon Configuration](DUNGEON_CONFIGURATION.md) - Customizing card pools
- [Quick Start Guide](QUICKSTART.md) - Getting started with PyScoundrel
