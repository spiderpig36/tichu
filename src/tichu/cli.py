from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static

from tichu import NUM_PLAYERS
from tichu.minimax_player import MiniMaxPlayer
from tichu.player import Player
from tichu.random_player import RandomPlayer
from tichu.tichu import InvalidPlayError, Tichu


class TichuCliApp(App[None]):
    """Render and run a Textual CLI for a single Tichu round."""

    TITLE = "Tichu"
    SUB_TITLE = "Game CLI"

    def compose(self) -> ComposeResult:
        """Create the widgets used by the Tichu CLI screen.

        Returns:
            ComposeResult: The generated widget composition.
        """
        yield Header(show_clock=False)
        yield Static("Preparing game...", id="game-output")
        yield Footer()

    async def on_mount(self) -> None:
        """Run one game round when the app mounts and render the output."""
        output = self.query_one("#game-output", Static)
        output.update(self.run_round())

    def run_round(self) -> str:
        """Execute the existing round flow and return renderable text output.

        Returns:
            str: The output that mirrors the previous terminal main loop.
        """
        players: list[Player] = [
            RandomPlayer(f"RANDOM {i}") for i in range(NUM_PLAYERS - 1)
        ]
        players.append(MiniMaxPlayer("MINIMAX"))
        game = Tichu()
        game.new_game(players)
        game.start_new_round()
        for player_idx, player in enumerate(game.players):
            card_indices = player.get_push_play(game.state)
            game.push_cards(player_idx, card_indices)
        output_lines: list[str] = []
        while not game.end_of_round:
            output_lines.append(f"{game.current_player.name}'s turn:")
            output_lines.append(str(game.state))
            output_lines.append(
                str(game.state.get_player_state(game.state.current_player_idx))
            )
            output_lines.append("----------------------")
            play = game.current_player.get_card_play(game.state)
            try:
                game.next_turn(game.state.current_player_idx, play)
            except InvalidPlayError as error:
                output_lines.append(f"Invalid play: {error}")
        return "\n".join(output_lines)


def main() -> None:
    """Start the Textual CLI application."""
    TichuCliApp().run()


if __name__ == "__main__":
    main()
