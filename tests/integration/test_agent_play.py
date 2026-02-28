"""Integration tests for agent-driven complete game runs."""

import pytest
from pyscoundrel.game.engine import GameEngine
from .conftest import run_game

pytestmark = pytest.mark.integration


class TestAgentCompletesGame:
    def test_barehanded_agent_finishes_game(self, engine, barehanded_agent):
        state = run_game(engine, barehanded_agent)
        assert state.game_over is True

    def test_weapon_first_agent_finishes_game(self, engine, weapon_first_agent):
        state = run_game(engine, weapon_first_agent)
        assert state.game_over is True

    def test_game_ends_in_win_or_loss(self, engine, barehanded_agent):
        state = run_game(engine, barehanded_agent)
        assert state.game_over is True
        # Must be exactly one of win or loss
        assert state.victory is True or state.victory is False

    def test_turn_counter_increments(self, engine, barehanded_agent):
        state = run_game(engine, barehanded_agent)
        assert state.turn_number > 0

    def test_discard_pile_is_not_empty_after_game(self, engine, barehanded_agent):
        state = run_game(engine, barehanded_agent)
        assert len(state.discard_pile) > 0


class TestSeedReproducibility:
    def test_same_seed_produces_same_outcome(self, barehanded_agent):
        engine_a = GameEngine(seed=99)
        engine_b = GameEngine(seed=99)
        state_a = run_game(engine_a, barehanded_agent)
        state_b = run_game(engine_b, barehanded_agent)
        assert state_a.victory == state_b.victory
        assert state_a.player.health == state_b.player.health
        assert state_a.turn_number == state_b.turn_number

    def test_different_seeds_can_produce_different_turn_counts(self, barehanded_agent):
        results = set()
        for seed in range(10):
            engine = GameEngine(seed=seed)
            state = run_game(engine, barehanded_agent)
            results.add(state.turn_number)
        # With 10 different seeds, game length should vary
        assert len(results) > 1

    def test_weapon_agent_outperforms_barehanded_agent(self, barehanded_agent, weapon_first_agent):
        # Run multiple seeds and compare average final health
        barehanded_healths = []
        weapon_healths = []
        for seed in range(20):
            engine_b = GameEngine(seed=seed)
            engine_w = GameEngine(seed=seed)
            state_b = run_game(engine_b, barehanded_agent)
            state_w = run_game(engine_w, weapon_first_agent)
            barehanded_healths.append(state_b.player.health)
            weapon_healths.append(state_w.player.health)
        avg_barehanded = sum(barehanded_healths) / len(barehanded_healths)
        avg_weapon = sum(weapon_healths) / len(weapon_healths)
        # Weapon agent should on average end with more health
        assert avg_weapon >= avg_barehanded
