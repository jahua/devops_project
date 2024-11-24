from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player
import string

class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        if self.state is None:
            raise ValueError("Game state has not been initialized")
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def print_state(self) -> None:
        """ Print the current game state """
        if not self.state:
            print("Game state is not initialized.")
            return

        masked_word = ''.join(
            letter if letter.lower() in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        # guessed = "".join([char if char in guessed_correctly else "_" for char in word])

        print(f"Word: {masked_word}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses: {', '.join(self.state.incorrect_guesses)}")
        print(f"Phase: {self.state.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        if self.state.phase != GamePhase.RUNNING:
            return []

        guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
        available_letters = set(string.ascii_uppercase) - {letter.upper() for letter in guessed_letters}

        return [GuessLetterAction(letter) for letter in sorted(available_letters)]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        if self.state is None or self.state.phase != GamePhase.RUNNING:
            raise ValueError("Game is not in a running phase.")

        letter = action.letter.lower()

        if letter in self.state.guesses or letter in self.state.incorrect_guesses:
            print(f"Letter '{letter}' has already been guessed.")
            return

        if letter in self.state.word_to_guess.lower():
            self.state.guesses.append(letter)
            print(f"Correct guess: {letter}")
        else:
            self.state.incorrect_guesses.append(letter)
            print(f"Incorrect guess: {letter}")

        # Check for game completion
        if all(
                letter in self.state.guesses or not letter.isalpha()
                for letter in self.state.word_to_guess.lower()
        ):
            self.state.phase = GamePhase.FINISHED
            print("Game over: You guessed the word!")
        elif len(self.state.incorrect_guesses) >= 6:  # Assuming 6 incorrect guesses as the limit
            self.state.phase = GamePhase.FINISHED
            print("Game over: Too many incorrect guesses!")

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player """
        if self.state is None:
            raise ValueError("Game state has not been initialized.")

        masked_word = ''.join(
            letter if letter.lower() in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )

        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.state.phase,
            guesses=self.state.guesses,
            incorrect_guesses=self.state.incorrect_guesses,
        )


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

class ConsolePlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            guess = input("Guess a letter: ").upper()
            # return the guessed letter as an GuessLetterAction
            return GuessLetterAction(guess)

        return None

if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Start the game
    game_state.phase = GamePhase.RUNNING
    game.print_state()

    # Random player example
    #player = RandomPlayer()
    # Console Player example
    player = ConsolePlayer()
    while game_state.phase == GamePhase.RUNNING:
        actions = game.get_list_action()
        action = player.select_action(game_state, actions)
        if action:
            game.apply_action(action)
            game.print_state()
