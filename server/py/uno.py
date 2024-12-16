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

    def __str__(self) -> str:
        s = self.color[0].upper() if self.color else ""
        if self.symbol is None:
            s += f'{self.number}'
        else:
            s += self.symbol.upper()
            if self.number is not None:
                s += f' {self.number}'
        return s


class Action(BaseModel):
    card: Optional[Card] = None
    color: Optional[str] = None
    draw: Optional[int] = None
    uno: bool = False

    def __lt__(self, other: 'Action') -> bool:
        return str(self) < str(other)

    def __str__(self) -> str:
        s = ''
        if self.card is not None:
            s += f'{self.card}'
        if self.color is not None and self.card is not None and self.card.symbol is not None:
            if len(s) > 0:
                s += ' '
            s += ' ' + self.color[0].upper()
        if self.draw is not None:
            if len(s) > 0:
                s += ' '
            s += f'+{self.draw}'
        if self.uno:
            if len(s) > 0:
                s += ' '
            s += f'UNO'
        return s


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

    list_card_draw: List[Card] = []
    list_card_discard: List[Card] = []
    list_player: List[PlayerState] = []
    phase: GamePhase = GamePhase.SETUP
    cnt_player: int = 2
    idx_player_active: Optional[int] = None
    direction: int = 1
    color: Optional[str] = None
    cnt_to_draw: int = 0
    has_drawn: bool = False

    def __str__(self) -> str:
        s = '  - Last Card: '
        s += self.color[0].upper() if self.color else ""
        if self.list_card_discard is None:
            s += 'None'
        else:
            card = self.list_card_discard[-1]
            if card.symbol is None:
                s += f'{card.number}'
            else:
                s += card.symbol.upper()
                if card.number is not None:
                    s += f' {card.number}'
        s += '\n'
        s += f'  - Color: {self.color}\n'
        s += f'  - Cnt To Draw: {self.cnt_to_draw}\n'
        s += f'  - Has Drawn: {self.has_drawn}\n'
        s += f'  - Direction: {self.direction}\n'
        s += f'  - Phase: {self.phase}\n'
        for i, player in enumerate(self.list_player):
            s += '    '
            s += '> ' if i == self.idx_player_active else '  '
            s += f'{player.name} ({len(player.list_card)}): '
            s += ", ".join([str(card) for card in player.list_card]) + '\n'
        return s[:-1]


class Uno(Game):

    def _is_card_playable(self, card_to_play: Card, top_card: Card) -> bool:
        """
        Determines if a card can be played on the current top card of the discard pile.

        Args:
            card_to_play (Card): The card the player intends to play.
            top_card (Card): The card currently on the top of the discard pile.

        Returns:
            bool: True if the card can be played, False otherwise.
        """
        # Wild cards are always playable
        if card_to_play.color == 'any':
            return True

        # Match by color
        if card_to_play.color == top_card.color:
            return True

        # Match by number (for numbered cards)
        if card_to_play.number is not None and card_to_play.number == top_card.number:
            return True

        # Match by symbol (for action cards like skip, reverse, draw2)
        if card_to_play.symbol is not None and card_to_play.symbol == top_card.symbol:
            return True

        # If none of the conditions are met, the card is not playable
        return False

    def set_state(self, state: GameState) -> None:
        self.state = state

        if not self.state.list_card_draw:
            self.state.list_card_draw = self.state.LIST_CARD.copy()
            random.shuffle(self.state.list_card_draw)
            print("[DEBUG] Initial draw pile shuffled with 108 cards.")

        if self.state.phase == GamePhase.SETUP:
            if self.state.idx_player_active is None:
                self.state.idx_player_active = 0

            if not self.state.list_card_draw:
                print("[DEBUG] No cards available in draw pile during setup.")
                return

            # Deal cards to players
            if len(self.state.list_player) < self.state.cnt_player:
                for p in range(self.state.cnt_player):
                    player = PlayerState(name=f"Player{p}")
                    for _ in range(self.state.CNT_HAND_CARDS):
                        if self.state.list_card_draw:
                            player.list_card.append(self.state.list_card_draw.pop())
                    self.state.list_player.append(player)
                print("[DEBUG] Cards dealt to players.")

            # Set the first discard pile card
            max_attempts = 100  # Safeguard to avoid infinite loops
            attempts = 0
            while attempts < max_attempts:
                initial_card = self.state.list_card_draw.pop()
                if initial_card.symbol != "wilddraw4":
                    self.state.list_card_discard = [initial_card]
                    self.state.color = initial_card.color
                    print(f"[DEBUG] First discard pile card set to {initial_card}.")

                    # Handle special effects of the first card
                    if initial_card.symbol == "reverse":
                        self.state.direction *= -1
                        print("[DEBUG] Direction reversed.")
                    elif initial_card.symbol == "skip":
                        self.state.idx_player_active = (
                                                               self.state.idx_player_active + 1
                                                       ) % self.state.cnt_player
                        print(f"[DEBUG] Player skipped. New active player: {self.state.idx_player_active}.")
                    elif initial_card.symbol == "draw2":
                        self.state.cnt_to_draw += 2
                        print(f"[DEBUG] Player must draw 2 cards. Pending draw count: {self.state.cnt_to_draw}.")
                    break
                else:
                    # Return WILD DRAW 4 card to the draw pile and reshuffle
                    self.state.list_card_draw.append(initial_card)
                    random.shuffle(self.state.list_card_draw)
                    print(
                        f"[DEBUG] WILD DRAW 4 card moved back to the draw pile and reshuffled. Attempt {attempts + 1}.")
                attempts += 1

            if attempts >= max_attempts:
                raise RuntimeError("Failed to initialize a valid first discard card after multiple attempts.")

            self.state.phase = GamePhase.RUNNING
            print("[DEBUG] Game phase set to RUNNING.")

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        print('----------------')
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
        current_player = self.state.list_player[self.state.idx_player_active or 0]

        # Add safety check for empty discard pile
        if not self.state.list_card_discard:
            return []

        current_card = self.state.list_card_discard[-1]

        # If we have any pending draws (cnt_to_draw > 0), handle those scenarios first
        if self.state.cnt_to_draw > 0:
            # If cnt_to_draw > 2, must only draw the accumulated cards (e.g. 4)
            if self.state.cnt_to_draw > 2:
                return [Action(draw=self.state.cnt_to_draw)]

            # If cnt_to_draw == 2 and top card is draw2, we can stack another draw2 if available
            if self.state.cnt_to_draw == 2 and current_card.symbol == "draw2":

                draw2_cards = [
                    c for c in current_player.list_card if c.symbol == "draw2"
                ]
                if draw2_cards:
                    # If we can stack another draw2, show ONLY the stacking actions (no normal draw)
                    stack_actions = []
                    for card in draw2_cards:
                        if len(current_player.list_card) == 2:
                            stack_actions.append(
                                Action(card=card, color=card.color, draw=4, uno=True)
                            )
                            stack_actions.append(
                                Action(card=card, color=card.color, draw=4, uno=False)
                            )
                        else:
                            stack_actions.append(
                                Action(card=card, color=card.color, draw=4)
                            )

                    # No stacking wanted
                    stack_actions.append(
                        Action(draw=self.state.cnt_to_draw)
                    )

                    return stack_actions
                else:
                    # No stack possible, must just draw the 2 cards
                    return [Action(draw=self.state.cnt_to_draw)]

            # If cnt_to_draw > 0 but not equal to 2 scenario (like cnt_to_draw=1 or another unusual case)
            # Just return the forced draw action
            return [Action(draw=self.state.cnt_to_draw)]

        # If we reach here, cnt_to_draw == 0, proceed with normal logic
        # Special case: if first card is wild and only one card on discard
        if current_card.symbol == "wild" and len(self.state.list_card_discard) == 1:
            playable_found = False
            for card in current_player.list_card:
                if len(current_player.list_card) == 2:
                    actions.append(Action(card=card, color=card.color, uno=True))
                    actions.append(Action(card=card, color=card.color, uno=False))
                else:
                    actions.append(Action(card=card, color=card.color))
                playable_found = True
            if not self.state.has_drawn:
                actions.append(Action(draw=1))
            return actions

        # Normal matching scenario
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
                # Can only play if no matching color card in hand
                if not any(
                        c.color == self.state.color
                        for c in current_player.list_card
                        if c != card and c.color != "any"
                ):
                    for col in ["red", "green", "yellow", "blue"]:
                        if len(current_player.list_card) == 2:
                            actions.append(
                                Action(card=card, color=col, draw=4, uno=True)
                            )
                            actions.append(
                                Action(card=card, color=col, draw=4, uno=False)
                            )
                        else:
                            actions.append(Action(card=card, color=col, draw=4))
                    playable_found = True
            else:
                # Match by color, number, or symbol
                if (
                        card.color == self.state.color
                        or (card.symbol and card.symbol == current_card.symbol)
                        or (
                        card.number is not None
                        and current_card.number is not None
                        and card.number == current_card.number
                )
                ):
                    if card.symbol == "draw2":
                        # normal draw2 when cnt_to_draw=0
                        if len(current_player.list_card) == 2:
                            actions.append(
                                Action(card=card, color=card.color, draw=2, uno=True)
                            )
                            actions.append(
                                Action(card=card, color=card.color, draw=2, uno=False)
                            )
                        else:
                            actions.append(Action(card=card, color=card.color, draw=2))
                    else:
                        if len(current_player.list_card) == 2:
                            actions.append(
                                Action(card=card, color=card.color, uno=True)
                            )
                            actions.append(
                                Action(card=card, color=card.color, uno=False)
                            )
                        else:
                            actions.append(Action(card=card, color=card.color))
                    playable_found = True

        if not self.state.has_drawn:
            actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        current_player = self.state.list_player[self.state.idx_player_active or 0]

        def move_to_next_player() -> None:
            self.state.idx_player_active = ((self.state.idx_player_active or 0) + self.state.direction
                                            ) % self.state.cnt_player
            self.state.has_drawn = False

        if action and action.card:
            current_player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            self.state.color = action.color if action.color else action.card.color

            if action.card.symbol == "reverse":
                self.state.direction *= -1
            elif action.card.symbol == "skip":
                self.state.idx_player_active = ((self.state.idx_player_active or 0) + 2 * self.state.direction
                                                ) % self.state.cnt_player
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
        elif action and action.draw:
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

        move_to_next_player()

    def get_player_view(self, idx_player: Optional[int]) -> GameState:
        masked_state = self.state.model_copy(deep=True)
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(color=None, number=None, symbol=None)] * len(
                    player.list_card
                )
        if masked_state.list_card_draw:
            masked_state.list_card_draw = [
                                              Card(color=None, number=None, symbol=None)
                                          ] * len(masked_state.list_card_draw)
        return masked_state


class RandomPlayer(Player):
    def select_action(
            self, state: GameState, actions: List[Action]
    ) -> Optional[Action]:
        my_actions = actions
        if my_actions:
            if len(my_actions) > 1:
                for my_action in my_actions:
                    if my_action.draw == 1:
                        my_actions.remove(my_action)
                        break
            return random.choice(my_actions)
        return None


if __name__ == "__main__":
    uno = Uno()
    state = GameState(
        cnt_player=3, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    uno.set_state(state)
    players = [RandomPlayer() for _ in range(state.cnt_player)]

    while uno.get_state().phase == GamePhase.RUNNING:
        current_state = uno.get_state()
        current_player_idx = current_state.idx_player_active
        player_view = uno.get_player_view(current_player_idx)
        actions = uno.get_list_action()
        action = players[current_player_idx or 0].select_action(player_view, actions)
        uno.apply_action(action)
        uno.print_state()

    final_state = uno.get_state()
    winner = final_state.idx_player_active
    print(f"\nGame Over! Player {winner} wins!")
