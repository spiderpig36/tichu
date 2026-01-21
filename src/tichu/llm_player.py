import logging
import os
import random
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES
from tichu.player import Play, Player


class InvalidLLMResponse(Exception):
    """Raised when the LLM returns an invalid response."""


class LLMPlay(BaseModel):
    play: Literal["pass", "tichu"] | list[int]


class LLMPlayer(Player):
    def __init__(self, name: str = "Anonymous"):
        super().__init__(name)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def get_card_play(self):
        # Load rules from file
        rules_path = os.path.join(os.path.dirname(__file__), "..", "..", "rules.md")
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = f.read()

        prompt = f"""
Game Rules:
{rules}

Your Name: {self.name}

{self}

{self.game_state}

Instructions: Decide what to play based on the rules and state. Respond with exactly one of:
- 'pass' to pass your turn
- 'tichu' to call Tichu (only if you have a full hand and haven't called Grand Tichu)
- Comma-separated list of card indices (0-based, e.g., '0,1,2') to play those cards from your hand

Ensure the play is valid according to the rules.
"""

        response = self.client.responses.parse(
            text_format=LLMPlay,
            model="gpt-4o-2024-08-06",
            input=[{"role": "user", "content": prompt}],
        )

        if not response or not response.output_parsed:
            raise InvalidLLMResponse("No response from LLM")
        answer = response.output_parsed.play
        if answer == "pass":
            return "pass"
        elif answer == "tichu":
            return "tichu"
        if answer and all(0 <= idx < len(self.state.hand) for idx in answer):
            return set(answer)
        raise InvalidLLMResponse(f"Invalid card indices: {answer}")

    def get_grand_tichu_play(self):
        # TODO: Implement LLM grand tichu play
        return "pass"

    def get_dragon_stack_recipient_play(self) -> int:
        # TODO: Implement LLM dragon stack recipient play
        return random.randint(0, NUM_PLAYERS - 1)

    def get_mahjong_wish_play(self) -> int:
        # TODO: Implement LLM mahjong wish play
        return random.choice(NORMAL_CARD_VALUES)

    def get_push_play(self) -> set[int]:
        # TODO: Implement LLM push play
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
