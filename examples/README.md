# Example Agents

This directory contains example agents demonstrating how to create automated players for PyScoundrel.

## Available Examples

### 1. [my_agent.py](my_agent.py) - Simple Agent
A basic agent that demonstrates the minimum implementation:
- Never avoids rooms
- Always chooses the first available card
- Uses weapon if available

**Run:**
```bash
python -m pyscoundrel --agent examples/my_agent.py --seed 42
```

### 2. [smart_agent.py](smart_agent.py) - Strategic Agent
A more sophisticated agent with strategic decision-making:
- Avoids rooms when health is below 8
- Prioritizes potions when injured (health < 15)
- Grabs weapons if unarmed
- Uses weapons on killable monsters
- Chooses lowest-damage monsters when fighting barehanded

**Run:**
```bash
python -m pyscoundrel --agent examples/smart_agent.py --seed 42
```

**Run in headless mode (faster, no UI):**
```bash
python -m pyscoundrel --agent examples/smart_agent.py --seed 42 --headless
```

## Creating Your Own Agent

To create a custom agent:

1. Create a new Python file
2. Import the base Agent class:
   ```python
   from pyscoundrel.agents import Agent as BaseAgent
   from pyscoundrel.game.state import GameState
   from pyscoundrel.models import Card, CardType
   ```

3. Create a class that inherits from `Agent`:
   ```python
   class Agent(BaseAgent):
       def decide_avoid_room(self, state: GameState) -> bool:
           # Return True to avoid, False to face the room
           return False

       def choose_card(self, state: GameState, available_cards: list[Card]) -> tuple[int, str]:
           # Return (card_index, method)
           # method: "barehanded", "weapon", or "auto" for non-monsters
           return (0, "auto")
   ```

4. Run your agent:
   ```bash
   python -m pyscoundrel --agent your_agent.py
   ```

## Agent Interface

### `decide_avoid_room(state: GameState) -> bool`
Called when entering a new room to decide whether to avoid it.

**Parameters:**
- `state`: Current game state with player health, deck info, current room

**Returns:**
- `True` to avoid the room (if allowed)
- `False` to face the room

### `choose_card(state: GameState, available_cards: list[Card]) -> tuple[int, str]`
Called to choose which card to face and how to handle it.

**Parameters:**
- `state`: Current game state
- `available_cards`: List of cards not yet faced in current room

**Returns:**
- Tuple of `(card_index, method)` where:
  - `card_index`: Index in `available_cards` list (0-based)
  - `method`: One of:
    - `"barehanded"` - Fight monster without weapon
    - `"weapon"` - Fight monster with weapon
    - `"auto"` - For non-monsters (weapons/potions)

## Game State Access

The `GameState` object provides:
- `state.player.health` - Current health (max 20)
- `state.player.has_weapon` - Whether player has a weapon
- `state.player.equipped_weapon` - Current weapon (if any)
- `state.current_room` - Current room with 4 cards
- `state.deck.remaining` - Cards left in deck
- `state.can_avoid_room` - Whether avoiding is allowed

## Tips for Writing Agents

1. **Check weapon availability**:
   ```python
   if state.player.has_weapon:
       weapon = state.player.equipped_weapon
       if weapon.can_kill(monster):
           # Use weapon
   ```

2. **Prioritize survival**:
   - Grab potions when health is low
   - Avoid high-damage monsters early
   - Use weapons strategically

3. **Plan ahead**:
   - Check `state.deck.remaining` to know how much game is left
   - Consider weapon restrictions (can only kill ≤ last kill value)

4. **Test with different seeds**:
   ```bash
   python -m pyscoundrel --agent your_agent.py --seed 42
   python -m pyscoundrel --agent your_agent.py --seed 123
   ```

5. **Use headless mode for testing**:
   ```bash
   python -m pyscoundrel --agent your_agent.py --headless
   ```

## Debugging Your Agent

If your agent crashes or makes invalid moves, check:
- Card index is within `available_cards` range
- Combat method matches card type
- Weapon is available before choosing "weapon" method
- Avoid room logic respects `state.can_avoid_room`
