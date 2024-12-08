# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    color: Optional[str] = None   # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None   # the number of cards to draw for the next player
    uno: bool = False            # true to announce "UNO" with the second last card


class PlayerState(BaseModel):
    name: Optional[str] = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):
    # numbers of cards for each player to start with
    CNT_HAND_CARDS: int = 7
    # any = for wild cards
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    # draw2 = draw two cards, wild = chose color, wilddraw4 = chose color and draw 4
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    LIST_CARD: List[Card] = [
        Card(color='red', number=0), Card(color='green', number=0), Card(color='yellow', number=0), Card(color='blue', number=0),
        Card(color='red', number=1), Card(color='green', number=1), Card(color='yellow', number=1), Card(color='blue', number=1),
        Card(color='red', number=2), Card(color='green', number=2), Card(color='yellow', number=2), Card(color='blue', number=2),
        Card(color='red', number=3), Card(color='green', number=3), Card(color='yellow', number=3), Card(color='blue', number=3),
        Card(color='red', number=4), Card(color='green', number=4), Card(color='yellow', number=4), Card(color='blue', number=4),
        Card(color='red', number=5), Card(color='green', number=5), Card(color='yellow', number=5), Card(color='blue', number=5),
        Card(color='red', number=6), Card(color='green', number=6), Card(color='yellow', number=6), Card(color='blue', number=6),
        Card(color='red', number=7), Card(color='green', number=7), Card(color='yellow', number=7), Card(color='blue', number=7),
        Card(color='red', number=8), Card(color='green', number=8), Card(color='yellow', number=8), Card(color='blue', number=8),
        Card(color='red', number=9), Card(color='green', number=9), Card(color='yellow', number=9), Card(color='blue', number=9),
        # skip next player
        Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
        # revers playing direction
        Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
        # next player must draw 2 cards
        Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
        # current player choses color for next player to play
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        # current player choses color for next player to play and next player must draw 4 cards
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4'),
    ]

    list_card_draw: Optional[List[Card]] = []    # list of cards to draw
    list_card_discard: Optional[List[Card]] = [] # list of cards discarded
    list_player: List[PlayerState] = []         # list of player-states
    phase: GamePhase = GamePhase.SETUP          # the current game-phase
    cnt_player: int = 2                         # number of players N (to be set in the phase "setup")
    idx_player_active: Optional[int] = None     # the index (0 to N-1) of active player
    direction: int = 1                          # direction of the game, +1 to the left, -1 to right
    color: Optional[str] = None                 # active color (last card played or the chosen color after a wild cards)
    cnt_to_draw: int = 0                        # accumulated number of cards to draw for the next player
    has_drawn: bool = False                     # flag to indicate if the last player has already drawn cards or not


class Uno(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the number of players """
        state = GameState(cnt_player=3, phase=GamePhase.SETUP, direction= 1, idx_player_active=0)
        self.set_state(state)

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
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

            # Initialize discard pile
            initial_card = self.state.list_card_draw.pop()
            # Handle case of first discarded card is wild
            while initial_card.symbol == 'wilddraw4':
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

            if initial_card.symbol == 'reverse':
                self.state.direction *= -1
            elif initial_card.symbol == 'skip':
                self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
            elif initial_card.symbol == 'draw2':
                self.state.cnt_to_draw += 2
                # self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

            self.state.list_card_discard = [initial_card]
            self.state.color = initial_card.color
            self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    uno = Uno()
    state = GameState(cnt_player=3, idx_player_active=0, phase=GamePhase.SETUP)
    uno.set_state(state)
