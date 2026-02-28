"""Game constants for Scoundrel."""

# Game constants
STARTING_HP = 20
MAX_HP = 20
ROOM_SIZE = 4
CARDS_FACED_PER_TURN = 3
MAX_POTIONS_PER_TURN = 1

# Deck composition
TOTAL_CARDS = 44
MONSTER_COUNT = 26  # 13 Clubs + 13 Spades
WEAPON_COUNT = 9  # Diamonds 2-10
POTION_COUNT = 9  # Hearts 2-10

# Card value ranges
MONSTER_MIN = 2
MONSTER_MAX = 14  # Ace
WEAPON_MIN = 2
WEAPON_MAX = 10
POTION_MIN = 2
POTION_MAX = 10

# Card value names
CARD_NAMES = {
    11: "Jack",
    12: "Queen",
    13: "King",
    14: "Ace",
}
