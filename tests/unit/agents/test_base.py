"""Unit tests for pyscoundrel.agents.base"""

import pytest

from pyscoundrel.agents.base import Agent

pytestmark = pytest.mark.unit


class TestAgentIsAbstract:
    def test_cannot_instantiate_agent_directly(self):
        with pytest.raises(TypeError):
            Agent()

    def test_subclass_without_methods_cannot_be_instantiated(self):
        class IncompleteAgent(Agent):
            pass

        with pytest.raises(TypeError):
            IncompleteAgent()

    def test_subclass_missing_choose_card_cannot_be_instantiated(self):
        class PartialAgent(Agent):
            def decide_avoid_room(self, state):
                return False

        with pytest.raises(TypeError):
            PartialAgent()

    def test_subclass_missing_decide_avoid_room_cannot_be_instantiated(self):
        class PartialAgent(Agent):
            def choose_card(self, state, available_cards):
                return 0, "barehanded"

        with pytest.raises(TypeError):
            PartialAgent()

    def test_concrete_subclass_can_be_instantiated(self):
        class ConcreteAgent(Agent):
            def decide_avoid_room(self, state):
                return False

            def choose_card(self, state, available_cards):
                return 0, "barehanded"

        agent = ConcreteAgent()
        assert isinstance(agent, Agent)

    def test_concrete_agent_decide_avoid_room_returns_bool(self):
        class ConcreteAgent(Agent):
            def decide_avoid_room(self, state):
                return False

            def choose_card(self, state, available_cards):
                return 0, "barehanded"

        agent = ConcreteAgent()
        assert agent.decide_avoid_room(None) is False

    def test_concrete_agent_choose_card_returns_tuple(self):
        class ConcreteAgent(Agent):
            def decide_avoid_room(self, state):
                return False

            def choose_card(self, state, available_cards):
                return 0, "barehanded"

        agent = ConcreteAgent()
        idx, method = agent.choose_card(None, [])
        assert idx == 0
        assert method == "barehanded"
