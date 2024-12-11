import pytest
from server.py.hangman import Hangman, HangmanGameState, GuessLetterAction, GamePhase

def test_initialization():
    game = Hangman()
    assert game.state is None

def test_set_get_state():
    game = Hangman()
    state = HangmanGameState(word_to_guess='TEST', phase=GamePhase.RUNNING)
    game.set_state(state)
    assert game.get_state() == state

def test_action_list():
    game = Hangman()
    state = HangmanGameState(word_to_guess='TEST', phase=GamePhase.RUNNING)
    game.set_state(state)
    actions = game.get_list_action()
    assert len(actions) == 26  # All letters available
    assert all(action.letter.isupper() for action in actions)

def test_apply_action():
    game = Hangman()
    state = HangmanGameState(word_to_guess='TEST', phase=GamePhase.RUNNING)
    game.set_state(state)
    
    # Test correct guess
    game.apply_action(GuessLetterAction('T'))
    assert 'T' in game.state.guesses
    assert 'T' not in game.state.incorrect_guesses
    
    # Test incorrect guess
    game.apply_action(GuessLetterAction('X'))
    assert 'X' in game.state.incorrect_guesses

def test_game_ending():
    game = Hangman()
    state = HangmanGameState(word_to_guess='A', phase=GamePhase.RUNNING)
    game.set_state(state)
    
    # Test win condition
    game.apply_action(GuessLetterAction('A'))
    assert game.state.phase == GamePhase.FINISHED
    
    # Test lose condition
    game = Hangman()
    state = HangmanGameState(word_to_guess='Z', phase=GamePhase.RUNNING)
    game.set_state(state)
    for letter in 'ABCDEFGH':  # 8 incorrect guesses
        game.apply_action(GuessLetterAction(letter))
    assert game.state.phase == GamePhase.FINISHED 