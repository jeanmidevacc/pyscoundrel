"""Game state management for PyScoundrel."""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from ..models import Player, Deck, Room, Card


class GamePhase(Enum):
    """Current phase of the game."""

    SETUP = "setup"
    DRAW_ROOM = "draw_room"
    DECIDE_AVOID = "decide_avoid"
    FACE_CARDS = "face_cards"
    TURN_COMPLETE = "turn_complete"
    GAME_OVER = "game_over"


@dataclass
class GameState:
    """
    Complete state of a Scoundrel game.

    This class represents a snapshot of the game at any point in time.
    """

    player: Player
    deck: Deck
    current_room: Optional[Room] = None
    discard_pile: List[Card] = field(default_factory=list)
    phase: GamePhase = GamePhase.SETUP
    turn_number: int = 0
    rooms_avoided_consecutively: int = 0
    last_card_was_potion: bool = False
    game_over: bool = False
    victory: bool = False

    @property
    def can_avoid_room(self) -> bool:
        """Check if player can avoid the current room."""
        return self.rooms_avoided_consecutively < 1

    @property
    def score(self) -> int:
        """
        Calculate the current score.

        If alive and deck is empty: positive score = health
        If dead: negative score = sum of remaining monster damage
        """
        if self.game_over:
            if self.victory:
                # Bonus for finishing with max health and last card being a potion
                if self.player.health == self.player.max_health and self.last_card_was_potion:
                    # Would need to track last potion value - simplified here
                    return self.player.health
                return self.player.health
            else:
                # Player died - negative score from remaining monsters
                remaining_damage = sum(
                    card.value for card in self.deck.cards if card.card_type.name == "MONSTER"
                )
                return -(remaining_damage)
        return 0

    def discard(self, cards: List[Card]) -> None:
        """
        Add cards to the discard pile.

        Args:
            cards: Cards to discard
        """
        self.discard_pile.extend(cards)

    def start_new_turn(self) -> None:
        """Start a new turn."""
        self.turn_number += 1
        self.player.reset_turn_state()
        self.last_card_was_potion = False
        self.phase = GamePhase.DRAW_ROOM

    def end_turn(self) -> None:
        """Mark the current turn as complete."""
        self.phase = GamePhase.TURN_COMPLETE

    def mark_quit(self) -> None:
        """Mark the game as quit by user (counts as defeat)."""
        self.game_over = True
        self.victory = False
        self.phase = GamePhase.GAME_OVER

    def check_game_over(self) -> bool:
        """
        Check if the game is over.

        Game ends when:
        - Player's health reaches 0 (loss)
        - Deck is empty (victory)
        """
        if self.player.is_dead:
            self.game_over = True
            self.victory = False
            self.phase = GamePhase.GAME_OVER
            return True

        if self.deck.is_empty:
            self.game_over = True
            self.victory = True
            self.phase = GamePhase.GAME_OVER
            return True

        return False

    def __str__(self) -> str:
        return (
            f"Turn {self.turn_number} | {self.player} | "
            f"Deck: {self.deck.remaining} | Phase: {self.phase.value}"
        )

    def __repr__(self) -> str:
        return (
            f"GameState(turn={self.turn_number}, phase={self.phase.value}, "
            f"player_hp={self.player.health}, deck={self.deck.remaining})"
        )
