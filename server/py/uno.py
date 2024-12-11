import random
from enum import Enum
from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel


class Card(BaseModel):
    color: Optional[str] = None  # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None  # the number of cards to draw for the next player
    uno: bool = False  # true to announce "UNO" with the second last card

    def __lt__(self, other):
        # Define a way to compare Actions, for example, by their name or some other attribute
        return str(self) < str(other)


class PlayerState(BaseModel):
    name: Optional[str] = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = "setup"  # before the game has started
    RUNNING = "running"  # while the game is running
    FINISHED = "finished"  # when the game is finished


class GameState(BaseModel):
    # numbers of cards for each player to start with
    CNT_HAND_CARDS: int = 7
    # any = for wild cards
    LIST_COLOR: List[str] = ["red", "green", "yellow", "blue", "any"]
    # draw2 = draw two cards, wild = chose color, wilddraw4 = chose color and draw 4
    LIST_SYMBOL: List[str] = ["skip", "reverse", "draw2", "wild", "wilddraw4"]
    LIST_CARD: List[Card] = [
        Card(color="red", number=0),
        Card(color="green", number=0),
        Card(color="yellow", number=0),
        Card(color="blue", number=0),
        Card(color="red", number=1),
        Card(color="green", number=1),
        Card(color="yellow", number=1),
        Card(color="blue", number=1),
        Card(color="red", number=2),
        Card(color="green", number=2),
        Card(color="yellow", number=2),
        Card(color="blue", number=2),
        Card(color="red", number=3),
        Card(color="green", number=3),
        Card(color="yellow", number=3),
        Card(color="blue", number=3),
        Card(color="red", number=4),
        Card(color="green", number=4),
        Card(color="yellow", number=4),
        Card(color="blue", number=4),
        Card(color="red", number=5),
        Card(color="green", number=5),
        Card(color="yellow", number=5),
        Card(color="blue", number=5),
        Card(color="red", number=6),
        Card(color="green", number=6),
        Card(color="yellow", number=6),
        Card(color="blue", number=6),
        Card(color="red", number=7),
        Card(color="green", number=7),
        Card(color="yellow", number=7),
        Card(color="blue", number=7),
        Card(color="red", number=8),
        Card(color="green", number=8),
        Card(color="yellow", number=8),
        Card(color="blue", number=8),
        Card(color="red", number=9),
        Card(color="green", number=9),
        Card(color="yellow", number=9),
        Card(color="blue", number=9),
        Card(color="red", number=1),
        Card(color="green", number=1),
        Card(color="yellow", number=1),
        Card(color="blue", number=1),
        Card(color="red", number=2),
        Card(color="green", number=2),
        Card(color="yellow", number=2),
        Card(color="blue", number=2),
        Card(color="red", number=3),
        Card(color="green", number=3),
        Card(color="yellow", number=3),
        Card(color="blue", number=3),
        Card(color="red", number=4),
        Card(color="green", number=4),
        Card(color="yellow", number=4),
        Card(color="blue", number=4),
        Card(color="red", number=5),
        Card(color="green", number=5),
        Card(color="yellow", number=5),
        Card(color="blue", number=5),
        Card(color="red", number=6),
        Card(color="green", number=6),
        Card(color="yellow", number=6),
        Card(color="blue", number=6),
        Card(color="red", number=7),
        Card(color="green", number=7),
        Card(color="yellow", number=7),
        Card(color="blue", number=7),
        Card(color="red", number=8),
        Card(color="green", number=8),
        Card(color="yellow", number=8),
        Card(color="blue", number=8),
        Card(color="red", number=9),
        Card(color="green", number=9),
        Card(color="yellow", number=9),
        Card(color="blue", number=9),
        # skip next player
        Card(color="red", symbol="skip"),
        Card(color="green", symbol="skip"),
        Card(color="yellow", symbol="skip"),
        Card(color="blue", symbol="skip"),
        Card(color="red", symbol="skip"),
        Card(color="green", symbol="skip"),
        Card(color="yellow", symbol="skip"),
        Card(color="blue", symbol="skip"),
        # revers playing direction
        Card(color="red", symbol="reverse"),
        Card(color="green", symbol="reverse"),
        Card(color="yellow", symbol="reverse"),
        Card(color="blue", symbol="reverse"),
        Card(color="red", symbol="reverse"),
        Card(color="green", symbol="reverse"),
        Card(color="yellow", symbol="reverse"),
        Card(color="blue", symbol="reverse"),
        # next player must draw 2 cards
        Card(color="red", symbol="draw2"),
        Card(color="green", symbol="draw2"),
        Card(color="yellow", symbol="draw2"),
        Card(color="blue", symbol="draw2"),
        Card(color="red", symbol="draw2"),
        Card(color="green", symbol="draw2"),
        Card(color="yellow", symbol="draw2"),
        Card(color="blue", symbol="draw2"),
        # current player choses color for next player to play
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        # current player choses color for next player to play and next player must draw 4 cards
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
    ]

    list_card_draw: Optional[List[Card]] = []  # list of cards to draw
    list_card_discard: Optional[List[Card]] = []  # list of cards discarded
    list_player: List[PlayerState] = []  # list of player-states
    phase: GamePhase = GamePhase.SETUP  # the current game-phase
    cnt_player: int = 2  # number of players N (to be set in the phase "setup")
    idx_player_active: Optional[int] = None  # the index (0 to N-1) of active player
    direction: int = 1  # direction of the game, +1 to the left, -1 to right
    color: Optional[str] = (
        None  # active color (last card played or the chosen color after a wild cards)
    )
    cnt_to_draw: int = 0  # accumulated number of cards to draw for the next player
    has_drawn: bool = (
        False  # flag to indicate if the last player has already drawn cards or not
    )


class Uno(Game):
    def __init__(self) -> None:
        """Important: Game initialization also requires a set_state call to set the number of players"""
        state = GameState(
            cnt_player=3, phase=GamePhase.SETUP, direction=1, idx_player_active=0
        )
        self.set_state(state)

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state"""
        self.state = state
        if not self.state.list_card_draw:
            # Initialize draw pile
            self.state.list_card_draw = self.state.LIST_CARD.copy()
            random.shuffle(self.state.list_card_draw)

        if self.state.phase == GamePhase.SETUP:
            # set player0 as first player if idx_player_active is None
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0
            # TEST 002 - Game cannot be played if there is no card to draw
            if len(self.state.list_card_draw) == 0:
                return

            # If a card has already been discarded
            if len(self.state.list_card_discard) > 0:
                initial_card = self.state.list_card_discard[-1]
            else:
                # Initialize discard pile
                initial_card = self.state.list_card_draw.pop()
            # Handle case of first discarded card is wild
            while (
                initial_card.symbol == "wilddraw4"
                and len(self.state.list_card_discard) == 0
            ):
                self.state.list_card_draw.append(initial_card)
                random.shuffle(self.state.list_card_draw)
                initial_card = self.state.list_card_draw.pop()

            # Deal cards to players
            for _ in range(self.state.cnt_player):
                player = PlayerState(name=f"Player{_}")
                for _ in range(self.state.CNT_HAND_CARDS):
                    if len(self.state.list_card_draw) > 1:
                        player.list_card.append(self.state.list_card_draw.pop())
                self.state.list_player.append(player)

            if initial_card.symbol == "reverse":
                self.state.direction *= -1
            elif initial_card.symbol == "skip":
                self.state.idx_player_active = (
                    self.state.idx_player_active + 1
                ) % self.state.cnt_player
            elif initial_card.symbol == "draw2":
                self.state.cnt_to_draw += 2
                # self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

            # If a card has already been discarded
            if len(self.state.list_card_discard) == 0:
                self.state.list_card_discard = [initial_card]
            self.state.color = initial_card.color
            self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state"""
        return self.state

    def print_state(self) -> None:
        """Print the current game state"""
        print(f"Phase: {self.state.phase}")
        print(f"Active Player: {self.state.idx_player_active}")
        print(f"Direction: {'Left' if self.state.direction == 1 else 'Right'}")
        print(f"Current Color: {self.state.color}")
        if self.state.list_card_discard:
            print(f"Top Card: {self.state.list_card_discard[-1]}")
        for idx, player in enumerate(self.state.list_player):
            print(f"\nPlayer {idx}: {player.name}")
            print(f"Cards: {player.list_card}")

    def _is_valid_play(self, card: Card, current_card: Card) -> bool:
        """Check if a card can be played on top of the current card"""
        # Wild cards can always be played
        if card.symbol in ["wild", "wilddraw4"]:
            return True

        # Match by color
        if card.color == self.state.color:
            return True

        # Match by symbol (including SKIP, REVERSE, and DRAW2)
        if card.symbol and card.symbol == current_card.symbol:
            return True

        # Match by number
        if card.number is not None and current_card.number is not None:
            return card.number == current_card.number

        return False

    def get_list_action(self) -> List[Action]:
        """Get list of valid actions for the current player"""
        if self.state.phase != GamePhase.RUNNING:
            return []

        actions: List[Action] = []
        current_player = self.state.list_player[self.state.idx_player_active]
        current_card = self.state.list_card_discard[-1]

        # If player must draw cards, they can only draw
        if self.state.cnt_to_draw > 0:
            actions.append(Action(draw=self.state.cnt_to_draw))
            return actions

        # Special case: if first card on discard pile is WILD, player can play any card
        if current_card.symbol == "wild" and len(self.state.list_card_discard) == 1:
            for card in current_player.list_card:
                if len(current_player.list_card) == 2:
                    actions.append(Action(card=card, color=card.color, uno=True))
                    actions.append(Action(card=card, color=card.color, uno=False))
                else:
                    actions.append(Action(card=card, color=card.color))
            return actions

        # Normal play: check each card if it can be played
        for card in current_player.list_card:
            if self._is_valid_play(card, current_card):
                # For regular cards and special cards (except WILD and DRAW2)
                if card.symbol not in ["wild", "wilddraw4", "draw2"]:
                    if len(current_player.list_card) == 2:
                        actions.append(Action(card=card, color=card.color, uno=True))
                        actions.append(Action(card=card, color=card.color, uno=False))
                    else:
                        actions.append(Action(card=card, color=card.color))
                # For WILD cards
                elif card.symbol == "wild":
                    for color in ["red", "green", "yellow", "blue"]:
                        if len(current_player.list_card) == 2:
                            actions.append(Action(card=card, color=color, uno=True))
                            actions.append(Action(card=card, color=color, uno=False))
                        else:
                            actions.append(Action(card=card, color=color))
                # For WILD DRAW 4 cards (can only be played if no matching color)
                elif card.symbol == "wilddraw4" and not any(
                    c.color == self.state.color
                    for c in current_player.list_card
                    if c != card
                ):
                    for color in ["red", "green", "yellow", "blue"]:
                        if len(current_player.list_card) == 2:
                            actions.append(
                                Action(card=card, color=color, draw=4, uno=True)
                            )
                            actions.append(
                                Action(card=card, color=color, draw=4, uno=False)
                            )
                        else:
                            actions.append(Action(card=card, color=color, draw=4))
                # For DRAW 2 cards
                elif card.symbol == "draw2" and self._is_valid_play(card, current_card):
                    draw_value = self.state.cnt_to_draw + 2 if self.state.cnt_to_draw > 0 else 2
                    if len(current_player.list_card) == 2:
                        actions.append(
                            Action(card=card, color=card.color, draw=draw_value, uno=True)
                        )
                        actions.append(
                            Action(card=card, color=card.color, draw=draw_value, uno=False)
                        )
                    else:
                        actions.append(Action(card=card, color=card.color, draw=draw_value))

        # Add draw action if player hasn't drawn yet and there's no cnt_to_draw
        if not self.state.has_drawn:
            actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Action) -> None:
        """Apply the given action to the game"""
        if self.state.phase != GamePhase.RUNNING:
            return

        current_player = self.state.list_player[self.state.idx_player_active]

        def move_to_next_player():
            self.state.idx_player_active = (
                self.state.idx_player_active + self.state.direction
            ) % self.state.cnt_player
            self.state.has_drawn = False

        # if the player has drawn and still cannot play, move to next player
        if not action and self.state.has_drawn:
            move_to_next_player()
            return

        # Handle draw action
        if action.draw:
            cards_to_draw = action.draw
            while cards_to_draw > 0:
                if not self.state.list_card_draw:
                    # Reshuffle discard pile if draw pile is empty
                    if len(self.state.list_card_discard) > 1:
                        top_card = self.state.list_card_discard.pop()
                        self.state.list_card_draw = self.state.list_card_discard
                        self.state.list_card_discard = [top_card]
                        random.shuffle(self.state.list_card_draw)
                    else:
                        # No cards left to draw
                        break

                current_player.list_card.append(self.state.list_card_draw.pop())
                cards_to_draw -= 1

            self.state.has_drawn = True
            self.state.cnt_to_draw = 0
            return

        # Handle play card action
        if action.card:
            # Remove card from player's hand
            current_player.list_card.remove(action.card)
            # Add card to discard pile
            self.state.list_card_discard.append(action.card)
            # Update color (for wild cards)
            self.state.color = action.color if action.color else action.card.color
            # Handle special cards
            if action.card.symbol:
                if action.card.symbol == "reverse":
                    self.state.direction *= -1
                elif action.card.symbol == "skip":
                    self.state.idx_player_active = (
                        self.state.idx_player_active + 2 * self.state.direction
                    ) % self.state.cnt_player
                    return
                elif action.card.symbol == "draw2":
                    self.state.cnt_to_draw += 2
                elif action.card.symbol == "wilddraw4":
                    self.state.cnt_to_draw += 4

            # Check for game end
            if len(current_player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                return

            # Check for UNO announcement
            if len(current_player.list_card) == 1 and not action.uno:
                # Player forgot to say UNO, draw 4 cards
                for _ in range(4):
                    if self.state.list_card_draw:
                        current_player.list_card.append(self.state.list_card_draw.pop())

        # Move to next player
        move_to_next_player()

    def get_player_view(self, idx_player: int) -> GameState:
        """Get the masked state for the active player (e.g. the opponent's cards are face down)"""
        masked_state = self.state.model_copy(deep=True)

        # Hide other players' cards
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(color=None, number=None, symbol=None)] * len(
                    player.list_card
                )

        # Hide draw pile
        if masked_state.list_card_draw:
            masked_state.list_card_draw = [
                Card(color=None, number=None, symbol=None)
            ] * len(masked_state.list_card_draw)

        return masked_state


class RandomPlayer(Player):
    def select_action(
        self, state: GameState, actions: List[Action]
    ) -> Optional[Action]:
        """Given masked game state and possible actions, select the next action"""
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":
    uno = Uno()
    # Initialize the game state
    state = uno.get_state()
    # state.cnt_player = 3
    # uno.set_state(state)

    # Create players
    players = [RandomPlayer() for _ in range(state.cnt_player)]

    # Main game loop
    while uno.get_state().phase == GamePhase.RUNNING:
        current_state = uno.get_state()
        current_player_idx = current_state.idx_player_active

        # Get player view and possible actions
        player_view = uno.get_player_view(current_player_idx)
        actions = uno.get_list_action()

        # Get player's action
        action = players[current_player_idx].select_action(player_view, actions)
        # Apply the action
        uno.apply_action(action)
        # Print game state
        uno.print_state()

    # Game over
    final_state = uno.get_state()
    winner = final_state.idx_player_active
    print(f"\nGame Over! Player {winner} wins!")
