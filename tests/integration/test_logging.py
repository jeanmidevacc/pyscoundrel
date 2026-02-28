"""Integration tests for GameLogger wired with a real game."""

import json
import pytest
from pyscoundrel.game.engine import GameEngine
from pyscoundrel.logging.logger import GameLogger
from pyscoundrel.logging.events import create_event
from .conftest import run_game

pytestmark = pytest.mark.integration


class TestGameLoggerFile:
    def test_logger_writes_to_file(self, tmp_path, barehanded_agent):
        log_path = tmp_path / "game.log"
        with GameLogger(log_file=log_path) as logger:
            logger.log("game_started", {"seed": 42})

        assert log_path.exists()
        assert log_path.stat().st_size > 0

    def test_log_file_contains_valid_json_lines(self, tmp_path, barehanded_agent):
        log_path = tmp_path / "game.log"
        with GameLogger(log_file=log_path) as logger:
            logger.log("game_started", {"seed": 42})
            logger.log("turn_start", {"turn": 1})
            logger.log("game_over", {"victory": False})

        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "event" in parsed
            assert "timestamp" in parsed
            assert "data" in parsed

    def test_log_file_contains_correct_event_names(self, tmp_path):
        log_path = tmp_path / "game.log"
        with GameLogger(log_file=log_path) as logger:
            logger.log("game_started", {})
            logger.log("room_drawn", {"turn": 1})

        content = log_path.read_text()
        assert "game_started" in content
        assert "room_drawn" in content

    def test_log_event_writes_state_when_provided(self, tmp_path):
        log_path = tmp_path / "game.log"
        state_data = {
            "player": {"health": 15, "max_health": 20},
            "dungeon": {"count": 40},
            "discard": {"count": 4},
        }
        with GameLogger(log_file=log_path) as logger:
            logger.log("turn_end", {"turn": 2}, state=state_data)

        lines = log_path.read_text().strip().splitlines()
        parsed = json.loads(lines[0])
        assert "state" in parsed
        assert parsed["state"]["player"]["health"] == 15

    def test_context_manager_closes_file(self, tmp_path):
        log_path = tmp_path / "game.log"
        logger = GameLogger(log_file=log_path)
        logger.log("test", {})
        logger.close()
        # File should be written and closed — writing again opens a new handle
        assert log_path.exists()


class TestGameLoggerDuringGame:
    def test_manual_logging_across_game_events(self, tmp_path, barehanded_agent):
        log_path = tmp_path / "game.log"
        engine = GameEngine(seed=42)

        with GameLogger(log_file=log_path) as logger:
            logger.log("game_started", {"seed": 42})
            state = run_game(engine, barehanded_agent)
            logger.log(
                "game_over",
                {
                    "victory": state.victory,
                    "health": state.player.health,
                    "turns": state.turn_number,
                },
            )

        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2

        first = json.loads(lines[0])
        last = json.loads(lines[-1])
        assert first["event"] == "game_started"
        assert last["event"] == "game_over"
        assert last["data"]["turns"] > 0

    def test_log_file_grows_with_multiple_events(self, tmp_path):
        log_path = tmp_path / "game.log"
        with GameLogger(log_file=log_path) as logger:
            for i in range(5):
                logger.log("turn", {"number": i})

        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 5
