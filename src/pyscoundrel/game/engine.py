"""Game engine for PyScoundrel."""

from typing import Optional, TYPE_CHECKING
from .state import GameState, GamePhase
from .actions import Action, ActionType, ActionResult
from ..models import Player, Deck, Room, Weapon, Card, CardType
from ..dungeon import Dungeon

if TYPE_CHECKING:
    pass


class GameEngine:
    """
    The game engine handles all game logic and rules enforcement.

    This class processes player actions and updates game state accordingly.
    """

    def __init__(
        self,
        state: Optional[GameState] = None,
        seed: Optional[int] = None,
        dungeon: Optional[Dungeon] = None,
    ):
        """
        Initialize the game engine.

        Args:
            state: Optional existing game state to continue from
            seed: Optional random seed for deck shuffling
            dungeon: Optional dungeon configuration (loads default if not provided)
        """
        if state is None:
            # Always load dungeon - use default if not specified
            if dungeon is None:
                dungeon = Dungeon()  # Loads default_dungeon.yaml

            # Create deck from dungeon
            deck = Deck(dungeon, shuffle=True, seed=seed)

            player = Player()
            state = GameState(player=player, deck=deck)

        self.state = state

    def start_game(self) -> ActionResult:
        """Start a new game."""
        self.state.phase = GamePhase.DRAW_ROOM
        return ActionResult(success=True, message="Game started! Draw your first room.")

    def draw_room(self) -> ActionResult:
        """
        Draw 4 cards to form a room.

        If there's a leftover card from previous room, use it as the first card.
        """
        if self.state.phase not in (GamePhase.DRAW_ROOM, GamePhase.TURN_COMPLETE):
            return ActionResult(success=False, message="Cannot draw room in current phase.")

        # Create new room
        room = Room()

        # Add leftover card from previous room if exists
        if self.state.current_room and self.state.current_room.is_complete:
            leftover = self.state.current_room.get_remaining_card()
            if leftover:
                room.add_card(leftover)

        # Draw remaining cards to make 4
        cards_needed = 4 - len(room.cards)
        drawn_cards = self.state.deck.draw_multiple(cards_needed)

        for card in drawn_cards:
            room.add_card(card)

        if not room.is_full:
            # Deck ran out - game over
            self.state.check_game_over()
            return ActionResult(
                success=True,
                message="Dungeon complete! You survived!",
                metadata={"game_over": True, "victory": True},
            )

        self.state.current_room = room
        self.state.start_new_turn()
        self.state.phase = GamePhase.DECIDE_AVOID

        return ActionResult(success=True, message=f"Room drawn: {room}", metadata={"room": room})

    def avoid_room(self) -> ActionResult:
        """
        Avoid the current room by placing all 4 cards at bottom of deck.

        Can only avoid if haven't avoided the previous room.
        """
        if not self.state.can_avoid_room:
            return ActionResult(success=False, message="Cannot avoid two rooms in a row!")

        if not self.state.current_room or not self.state.current_room.is_full:
            return ActionResult(success=False, message="No complete room to avoid!")

        # Put all 4 cards at bottom of deck
        self.state.deck.add_to_bottom(self.state.current_room.cards)
        self.state.rooms_avoided_consecutively += 1
        self.state.current_room = None
        self.state.phase = GamePhase.DRAW_ROOM

        return ActionResult(
            success=True, message="Room avoided. Cards placed at bottom of dungeon."
        )

    def face_card(self, card_index: int) -> ActionResult:
        """
        Face a card from the current room.

        Args:
            card_index: Index of card to face (0-3)

        Returns:
            Result indicating what happened
        """
        if self.state.phase not in (GamePhase.DECIDE_AVOID, GamePhase.FACE_CARDS):
            return ActionResult(success=False, message="Cannot face card in current phase.")

        room = self.state.current_room
        if not room:
            return ActionResult(success=False, message="No room available!")

        # Update phase to facing cards
        if self.state.phase == GamePhase.DECIDE_AVOID:
            self.state.phase = GamePhase.FACE_CARDS
            self.state.rooms_avoided_consecutively = 0

        try:
            card = room.face_card(card_index)
        except (IndexError, ValueError) as e:
            return ActionResult(success=False, message=str(e))

        # Handle the card based on its type
        if card.card_type == CardType.WEAPON:
            return self._handle_weapon(card)
        elif card.card_type == CardType.HEALTH_POTION:
            return self._handle_potion(card)
        elif card.card_type == CardType.MONSTER:
            return self._handle_monster_encounter(card)

        return ActionResult(success=False, message="Unknown card type!")

    def fight_monster_barehanded(self, monster: Card) -> ActionResult:
        """
        Fight a monster without a weapon (take full damage).

        Args:
            monster: The monster to fight

        Returns:
            Result of the combat
        """
        damage = monster.value
        self.state.player.take_damage(damage)
        self.state.discard([monster])

        game_over = self.state.check_game_over()

        self._check_turn_complete()

        return ActionResult(
            success=True,
            message=f"Fought {monster} barehanded!",
            damage_taken=damage,
            metadata={"player_died": game_over and not self.state.victory},
        )

    def fight_monster_with_weapon(self, monster: Card) -> ActionResult:
        """
        Fight a monster with the equipped weapon.

        Args:
            monster: The monster to fight

        Returns:
            Result of the combat
        """
        weapon = self.state.player.equipped_weapon
        if not weapon:
            return ActionResult(success=False, message="No weapon equipped!")

        if not weapon.can_kill(monster):
            return ActionResult(
                success=False,
                message=f"Weapon cannot kill {monster} (last kill: {weapon.last_kill_value})!",
            )

        damage = weapon.attack(monster)
        self.state.player.take_damage(damage)

        game_over = self.state.check_game_over()

        self._check_turn_complete()

        message = f"Used {weapon.card} against {monster}!"
        if damage == 0:
            message += " No damage taken!"

        return ActionResult(
            success=True,
            message=message,
            damage_taken=damage,
            metadata={"player_died": game_over and not self.state.victory},
        )

    def _handle_weapon(self, weapon_card: Card) -> ActionResult:
        """Handle picking up a weapon."""
        new_weapon = Weapon(card=weapon_card)

        # Discard old weapon and any monsters on it
        old_weapon = self.state.player.equip_weapon(new_weapon)
        if old_weapon:
            cards_to_discard = [old_weapon.card] + old_weapon.slain_monsters
            self.state.discard(cards_to_discard)
            message = f"Equipped {weapon_card}! Discarded old weapon."
        else:
            message = f"Equipped {weapon_card}!"

        self._check_turn_complete()

        return ActionResult(success=True, message=message, metadata={"weapon": new_weapon})

    def _handle_potion(self, potion: Card) -> ActionResult:
        """Handle using a health potion."""
        # Can only use one potion per turn
        if self.state.player.potions_used_this_turn >= 1:
            self.state.discard([potion])
            self._check_turn_complete()
            return ActionResult(
                success=True, message=f"Discarded {potion} (already used a potion this turn)."
            )

        # Heal the player
        heal_amount = self.state.player.heal(potion.value)
        self.state.player.potions_used_this_turn += 1
        self.state.last_card_was_potion = True
        self.state.discard([potion])

        self._check_turn_complete()

        return ActionResult(success=True, message=f"Used {potion}!", health_gained=heal_amount)

    def _handle_monster_encounter(self, monster: Card) -> ActionResult:
        """
        Handle encountering a monster.

        Returns a result indicating the monster was encountered.
        Player must choose how to fight it.
        """
        weapon = self.state.player.equipped_weapon
        can_use_weapon = weapon and weapon.can_kill(monster)

        metadata = {"monster": monster, "can_use_weapon": can_use_weapon, "weapon": weapon}

        if can_use_weapon:
            message = f"Encountered {monster}! (Weapon available)"
        else:
            if weapon:
                message = f"Encountered {monster}! (Weapon cannot be used - must fight barehanded)"
            else:
                message = f"Encountered {monster}! (No weapon - must fight barehanded)"

        return ActionResult(success=True, message=message, metadata=metadata)

    def _check_turn_complete(self) -> None:
        """Check if the current turn is complete (3 cards faced)."""
        if self.state.current_room and self.state.current_room.is_complete:
            self.state.end_turn()

    @property
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.state.game_over

    @property
    def score(self) -> int:
        """Get the current score."""
        return self.state.score
