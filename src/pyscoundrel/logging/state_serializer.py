"""Serialize game state for logging."""

from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..game.state import GameState
    from ..models import Card


def serialize_card(card: "Card") -> str:
    """Serialize a card to string."""
    return card.name


def serialize_state(state: "GameState") -> Dict[str, Any]:
    """Serialize game state to dictionary."""
    player = state.player

    # Player state
    player_data: Dict[str, Any] = {"health": player.health, "max_health": 20}

    if player.has_weapon:
        weapon = player.equipped_weapon
        player_data["weapon"] = {
            "card": serialize_card(weapon.card),
            "value": weapon.card.value,
            "kills": [m.value for m in weapon.slain_monsters],
            "last_kill": weapon.last_kill_value,
        }
    else:
        player_data["weapon"] = None

    # Dungeon (deck) state
    dungeon_data = {
        "count": len(state.deck._cards),
        "cards": [serialize_card(c) for c in state.deck._cards],
    }

    # Discard pile state
    discard_data = {
        "count": len(state.discard_pile),
        "cards": [serialize_card(c) for c in state.discard_pile],
    }

    # Room state
    room_data: Optional[Dict[str, Any]] = None
    if state.current_room:
        room = state.current_room
        room_data = {
            "cards": [serialize_card(c) for c in room.cards],
            "faced": [serialize_card(c) for c in room.cards_faced],
            "remaining": [serialize_card(c) for c in room.cards if c not in room.cards_faced],
        }

    return {
        "player": player_data,
        "dungeon": dungeon_data,
        "discard": discard_data,
        "room": room_data,
    }
