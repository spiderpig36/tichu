import os
import random
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES
from tichu.player import Player
from tichu.tichu_state import CardPlay


class InvalidLLMResponse(Exception):
    """Raised when the LLM returns an invalid response."""


class LLMPlay(BaseModel):
    play: Literal["pass", "tichu"] | list[int]
    argument: int | None


class LLMPlayer(Player):
    def __init__(self, name: str = "Anonymous"):
        super().__init__(name)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def get_card_play(self) -> CardPlay:
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
- Tuple of 
    - List of card indices (0-based) to play those cards from your hand
    - Integer argument (for Dragon card recipient or Mah Jong wish) if applicable, else None.

Ensure the play is valid according to the rules.
"""

        response = self.client.responses.parse(
            text_format=LLMPlay,
            model="gpt-4o-2024-08-06",
            input=[{"role": "user", "content": prompt}],
        )

        if not response or not response.output_parsed:
            raise InvalidLLMResponse("No response from LLM")
        play = response.output_parsed.play
        if play == "pass":
            return "pass"
        elif play == "tichu":
            return "tichu"
        if play and all(0 <= idx < len(self.state.hand) for idx in play):
            argument = response.output_parsed.argument
            return {self.state.hand[idx] for idx in play}, argument
        raise InvalidLLMResponse(f"Invalid card indices: {play}")

    def get_grand_tichu_play(self):
        # TODO: Implement LLM grand tichu play
        return "pass"

    def get_push_play(self) -> set[int]:
        # TODO: Implement LLM push play
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
