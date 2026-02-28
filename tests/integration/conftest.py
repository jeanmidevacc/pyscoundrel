"""Shared fixtures and helpers for integration tests."""

import pytest
from typing import Tuple
from pyscoundrel.game.engine import GameEngine
from pyscoundrel.game.state import GameState
from pyscoundrel.agents.base import Agent
from pyscoundrel.models.card import Card, CardType


# ---------------------------------------------------------------------------
# Concrete agent implementations used across integration tests
# ---------------------------------------------------------------------------


class BarehandedAgent(Agent):
    """Never avoids rooms. Always fights barehanded. Picks first available card."""

    def decide_avoid_room(self, state: GameState) -> bool:
        return False

    def choose_card(self, state: GameState, available_cards: list) -> Tuple[int, str]:
        return 0, "barehanded"


class WeaponFirstAgent(Agent):
    """
    Prefers to pick up weapons, then uses them.
    Falls back to barehanded for monsters when no weapon is available.
    Never avoids rooms.
    """

    def decide_avoid_room(self, state: GameState) -> bool:
        return False

    def choose_card(self, state: GameState, available_cards: list) -> Tuple[int, str]:
        # Prefer weapons first
        for i, card in enumerate(available_cards):
            if card.card_type == CardType.WEAPON:
                return i, "auto"
        # Then potions
        for i, card in enumerate(available_cards):
            if card.card_type == CardType.HEALTH_POTION:
                return i, "auto"
        # Then monsters — use weapon if available and able
        for i, card in enumerate(available_cards):
            if card.card_type == CardType.MONSTER:
                weapon = state.player.equipped_weapon
                if weapon and weapon.can_kill(card):
                    return i, "weapon"
                return i, "barehanded"
        return 0, "barehanded"


# ---------------------------------------------------------------------------
# Game runner helper
# ---------------------------------------------------------------------------


def run_game(engine: GameEngine, agent: Agent, max_turns: int = 300) -> GameState:
    """
    Drive a complete game with an agent until game over or max_turns.

    Mirrors the action sequence in __main__.py's agent mode:
    1. draw_room
    2. agent.decide_avoid_room  → avoid_room or face 3 cards
    3. For each card: agent.choose_card → face_card + optional combat
    """
    engine.start_game()
    turns = 0

    while not engine.is_game_over and turns < max_turns:
        result = engine.draw_room()
        if engine.is_game_over:
            break

        state = engine.state
        room = state.current_room

        # Avoid or face
        if agent.decide_avoid_room(state) and state.can_avoid_room:
            engine.avoid_room()
            turns += 1
            continue

        # Face 3 cards
        while not engine.is_game_over and not room.is_complete:
            available = room.available_cards
            card_idx, method = agent.choose_card(state, available)

            chosen_card = available[card_idx]
            room_idx = room.cards.index(chosen_card)

            result = engine.face_card(room_idx)
            if not result.success:
                break

            if result.metadata and "monster" in result.metadata:
                monster = result.metadata["monster"]
                can_use_weapon = result.metadata.get("can_use_weapon", False)
                if method == "weapon" and can_use_weapon:
                    engine.fight_monster_with_weapon(monster)
                else:
                    engine.fight_monster_barehanded(monster)

        turns += 1

    return engine.state


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    return GameEngine(seed=42)


@pytest.fixture
def started_engine(engine):
    engine.start_game()
    engine.draw_room()
    return engine


@pytest.fixture
def barehanded_agent():
    return BarehandedAgent()


@pytest.fixture
def weapon_first_agent():
    return WeaponFirstAgent()
