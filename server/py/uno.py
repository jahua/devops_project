"""UNO Card Game Implementation

This module implements the classic UNO card game with support for:
- 2+ players
- All standard cards (numbers, skip, reverse, draw2, wild, wilddraw4)
- Standard UNO rules including card stacking and UNO calls
"""

import random
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from server.py.game import Game, Player

class Card(BaseModel):
    color: Optional[str] = None
    number: Optional[int] = None
    symbol: Optional[str] = None

class Action(BaseModel):
    card: Optional[Card] = None
    color: Optional[str] = None
    draw: Optional[int] = None
    uno: bool = False

    def __lt__(self, other):
        return str(self) < str(other)

class PlayerState(BaseModel):
    name: Optional[str] = None
    list_card: List[Card] = []

class GamePhase(str, Enum):
    SETUP = "setup"
    RUNNING = "running"
    FINISHED = "finished"

class GameState(BaseModel):
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ["red", "green", "yellow", "blue", "any"]
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
        # skip
        Card(color="red", symbol="skip"),
        Card(color="green", symbol="skip"),
        Card(color="yellow", symbol="skip"),
        Card(color="blue", symbol="skip"),
        Card(color="red", symbol="skip"),
        Card(color="green", symbol="skip"),
        Card(color="yellow", symbol="skip"),
        Card(color="blue", symbol="skip"),
        # reverse
        Card(color="red", symbol="reverse"),
        Card(color="green", symbol="reverse"),
        Card(color="yellow", symbol="reverse"),
        Card(color="blue", symbol="reverse"),
        Card(color="red", symbol="reverse"),
        Card(color="green", symbol="reverse"),
        Card(color="yellow", symbol="reverse"),
        Card(color="blue", symbol="reverse"),
        # draw2
        Card(color="red", symbol="draw2"),
        Card(color="green", symbol="draw2"),
        Card(color="yellow", symbol="draw2"),
        Card(color="blue", symbol="draw2"),
        Card(color="red", symbol="draw2"),
        Card(color="green", symbol="draw2"),
        Card(color="yellow", symbol="draw2"),
        Card(color="blue", symbol="draw2"),
        # wild
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        Card(color="any", symbol="wild"),
        # wilddraw4
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
        Card(color="any", symbol="wilddraw4"),
    ]

    list_card_draw: Optional[List[Card]] = []
    list_card_discard: Optional[List[Card]] = []
    list_player: List[PlayerState] = []
    phase: GamePhase = GamePhase.SETUP
    cnt_player: int = 2
    idx_player_active: Optional[int] = None
    direction: int = 1
    color: Optional[str] = None
    cnt_to_draw: int = 0
    has_drawn: bool = False

class Uno(Game):
    def __init__(self) -> None:
        state = GameState(cnt_player=3, phase=GamePhase.SETUP, direction=1, idx_player_active=0)
        self.set_state(state)

    def set_state(self, state: GameState) -> None:
        self.state = state

        if not self.state.list_card_draw:
            self.state.list_card_draw = self.state.LIST_CARD.copy()
            random.shuffle(self.state.list_card_draw)

        if self.state.phase == GamePhase.SETUP:
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0

            if len(self.state.list_card_draw) == 0:
                return

            if len(self.state.list_card_discard) == 0:
                initial_card = self.state.list_card_draw.pop()
                while initial_card.symbol == "wilddraw4" and len(self.state.list_card_discard) == 0:
                    self.state.list_card_draw.append(initial_card)
                    random.shuffle(self.state.list_card_draw)
                    initial_card = self.state.list_card_draw.pop()

                for p in range(self.state.cnt_player):
                    player = PlayerState(name=f"Player{p}")
                    for _ in range(self.state.CNT_HAND_CARDS):
                        if len(self.state.list_card_draw) > 0:
                            player.list_card.append(self.state.list_card_draw.pop())
                    self.state.list_player.append(player)

                self.state.list_card_discard = [initial_card]
                self.state.color = initial_card.color
                if initial_card.symbol == "reverse":
                    self.state.direction *= -1
                elif initial_card.symbol == "skip":
                    self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
                elif initial_card.symbol == "draw2":
                    self.state.cnt_to_draw += 2
            else:
                if len(self.state.list_player) < self.state.cnt_player:
                    for p in range(self.state.cnt_player):
                        player = PlayerState(name=f"Player{p}")
                        for _ in range(self.state.CNT_HAND_CARDS):
                            if len(self.state.list_card_draw) > 0:
                                player.list_card.append(self.state.list_card_draw.pop())
                        self.state.list_player.append(player)
                initial_card = self.state.list_card_discard[-1]
                self.state.color = initial_card.color

            self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        print(f"Phase: {self.state.phase}")
        print(f"Active Player: {self.state.idx_player_active}")
        print(f"Direction: {'Left' if self.state.direction == 1 else 'Right'}")
        print(f"Current Color: {self.state.color}")
        if self.state.list_card_discard:
            print(f"Top Card: {self.state.list_card_discard[-1]}")
        for idx, player in enumerate(self.state.list_player):
            print(f"\nPlayer {idx}: {player.name}")
            print(f"Cards: {player.list_card}")

    def get_list_action(self) -> List[Action]:
        if self.state.phase != GamePhase.RUNNING:
            return []
        actions: List[Action] = []
        current_player = self.state.list_player[self.state.idx_player_active]
        current_card = self.state.list_card_discard[-1]

        # Handle first WILD card scenario (Test 010 fix)
        if current_card.symbol == "wild" and len(self.state.list_card_discard) == 1:
            playable_found = False
            for card in current_player.list_card:
                # Any card can be played after a WILD first card
                if len(current_player.list_card) == 2:
                    actions.append(Action(card=card, color=card.color, uno=True))
                    actions.append(Action(card=card, color=card.color, uno=False))
                else:
                    actions.append(Action(card=card, color=card.color))
                playable_found = True
            # Only add draw if no playable card was found
            if not playable_found and not self.state.has_drawn:
                actions.append(Action(draw=1))
            return actions

        # Handle draw2 stacking (Test 013 fix)
        if current_card.symbol == "draw2" and self.state.cnt_to_draw > 0:
            if self.state.cnt_to_draw == 2:
                # Only allow stacking on the first draw2
                draw2_cards = [c for c in current_player.list_card if c.symbol == "draw2"]
                if draw2_cards:
                    for card in draw2_cards:
                        if len(current_player.list_card) == 2:
                            actions.append(Action(card=card, color=card.color, draw=self.state.cnt_to_draw + 2, uno=True))
                            actions.append(Action(card=card, color=card.color, draw=self.state.cnt_to_draw + 2, uno=False))
                        else:
                            actions.append(Action(card=card, color=card.color, draw=self.state.cnt_to_draw + 2))
                else:
                    # No stack possible, must draw
                    actions.append(Action(draw=self.state.cnt_to_draw))
            else:
                # cnt_to_draw > 2 means already stacked, must now draw
                actions.append(Action(draw=self.state.cnt_to_draw))
            return actions

        # If cnt_to_draw > 0 and not in a stacking scenario
        if self.state.cnt_to_draw > 0:
            actions.append(Action(draw=self.state.cnt_to_draw))
            return actions

        # Normal play
        playable_found = False
        for card in current_player.list_card:
            if card.symbol == "wild":
                for col in ["red", "green", "yellow", "blue"]:
                    if len(current_player.list_card) == 2:
                        actions.append(Action(card=card, color=col, uno=True))
                        actions.append(Action(card=card, color=col, uno=False))
                    else:
                        actions.append(Action(card=card, color=col))
                playable_found = True
            elif card.symbol == "wilddraw4":
                if not any(c.color == self.state.color for c in current_player.list_card if c != card and c.color != 'any'):
                    for col in ["red", "green", "yellow", "blue"]:
                        if len(current_player.list_card) == 2:
                            actions.append(Action(card=card, color=col, draw=4, uno=True))
                            actions.append(Action(card=card, color=col, draw=4, uno=False))
                        else:
                            actions.append(Action(card=card, color=col, draw=4))
                    playable_found = True
            else:
                # match by color, number or symbol
                if (card.color == self.state.color or
                    (card.symbol is not None and card.symbol == current_card.symbol) or
                    (card.number is not None and current_card.number is not None and card.number == current_card.number)):
                    if card.symbol == "draw2":
                        if len(current_player.list_card) == 2:
                            actions.append(Action(card=card, color=card.color, draw=2, uno=True))
                            actions.append(Action(card=card, color=card.color, draw=2, uno=False))
                        else:
                            actions.append(Action(card=card, color=card.color, draw=2))
                    else:
                        if len(current_player.list_card) == 2:
                            actions.append(Action(card=card, color=card.color, uno=True))
                            actions.append(Action(card=card, color=card.color, uno=False))
                        else:
                            actions.append(Action(card=card, color=card.color))
                    playable_found = True

        # Only add draw action if player hasn't drawn yet and no forced scenario
        if not self.state.has_drawn:
            actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Action) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        current_player = self.state.list_player[self.state.idx_player_active]

        def move_to_next_player():
            self.state.idx_player_active = (self.state.idx_player_active + self.state.direction) % self.state.cnt_player
            self.state.has_drawn = False

        if action and action.draw:
            cards_to_draw = action.draw
            while cards_to_draw > 0:
                if not self.state.list_card_draw:
                    if len(self.state.list_card_discard) > 1:
                        top_card = self.state.list_card_discard.pop()
                        self.state.list_card_draw = self.state.list_card_discard
                        self.state.list_card_discard = [top_card]
                        random.shuffle(self.state.list_card_draw)
                    else:
                        break
                current_player.list_card.append(self.state.list_card_draw.pop())
                cards_to_draw -= 1
            self.state.has_drawn = True
            self.state.cnt_to_draw = 0
            return

        if action and action.card:
            current_player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            self.state.color = action.color if action.color else action.card.color

            if action.card.symbol == "reverse":
                self.state.direction *= -1
            elif action.card.symbol == "skip":
                self.state.idx_player_active = (self.state.idx_player_active + 2 * self.state.direction) % self.state.cnt_player
                if len(current_player.list_card) == 0:
                    self.state.phase = GamePhase.FINISHED
                return
            elif action.card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif action.card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

            if len(current_player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                return

            if len(current_player.list_card) == 1 and not action.uno:
                for _ in range(4):
                    if self.state.list_card_draw:
                        current_player.list_card.append(self.state.list_card_draw.pop())

        move_to_next_player()

    def get_player_view(self, idx_player: int) -> GameState:
        masked_state = self.state.model_copy(deep=True)
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(color=None, number=None, symbol=None)] * len(player.list_card)
        if masked_state.list_card_draw:
            masked_state.list_card_draw = [Card(color=None, number=None, symbol=None)] * len(masked_state.list_card_draw)
        return masked_state

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

if __name__ == "__main__":
    uno = Uno()
    state = uno.get_state()
    players = [RandomPlayer() for _ in range(state.cnt_player)]

    while uno.get_state().phase == GamePhase.RUNNING:
        current_state = uno.get_state()
        current_player_idx = current_state.idx_player_active
        player_view = uno.get_player_view(current_player_idx)
        actions = uno.get_list_action()
        action = players[current_player_idx].select_action(player_view, actions)
        uno.apply_action(action)
        uno.print_state()

    final_state = uno.get_state()
    winner = final_state.idx_player_active
    print(f"\nGame Over! Player {winner} wins!")
