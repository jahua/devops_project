import pytest
from server.py.uno import Uno, GamePhase, Card, PlayerState, GameState, Action


def test_initial_game_state():
    """Test 001: Validate values of initial game state (cnt_players=2)"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    assert state.cnt_player == 2
    assert state.phase == GamePhase.RUNNING
    assert state.idx_player_active == 0
    assert state.direction == 1
    assert len(state.list_player) == 2
    
    # Each player should have 7 cards initially
    for player in state.list_player:
        assert len(player.list_card) == 7

def test_card_values():
    """Test 002: Validate card values"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    valid_colors = ['red', 'green', 'yellow', 'blue', 'any']
    valid_symbols = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    
    # Check all cards in deck
    for card in state.LIST_CARD:
        assert card.color in valid_colors
        if card.number is not None:
            assert 0 <= card.number <= 9
        if card.symbol is not None:
            assert card.symbol in valid_symbols

def test_card_matching_simple():
    """Test 003: Test player card matching with discard pile card - simple cards"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Test matching by color
    top_card = Card(color='red', number=5, symbol=None)
    matching_card = Card(color='red', number=7, symbol=None)
    non_matching_card = Card(color='blue', number=2, symbol=None)
    
    assert game._is_card_playable(matching_card, top_card)
    assert game._is_card_playable(Card(color='red', number=5, symbol=None), top_card)  # Same number
    assert not game._is_card_playable(non_matching_card, top_card)

def test_card_matching_special():
    """Test 004: Test player card matching with discard pile card - special cards"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)

    # Test wild cards
    top_card = Card(color='red', number=5, symbol=None)
    wild_card = Card(color='any', number=None, symbol='wild')
    wild_draw4 = Card(color='any', number=None, symbol='wilddraw4')
    
    assert game._is_card_playable(wild_card, top_card)
    assert game._is_card_playable(wild_draw4, top_card)
    
    # Test special cards matching
    special_card = Card(color='red', number=None, symbol='skip')
    matching_special = Card(color='red', number=None, symbol='draw2')
    non_matching_special = Card(color='blue', number=None, symbol='reverse')
    
    assert game._is_card_playable(special_card, special_card)  # Same color
    assert game._is_card_playable(matching_special, special_card)  # Same color
    assert not game._is_card_playable(non_matching_special, special_card)  # Different color

def test_game_flow():
    """Test game flow and state transitions"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    # Verify initial state
    assert state.phase == GamePhase.RUNNING
    assert state.idx_player_active == 0
    
    # Test playing a card
    player = state.list_player[0]
    if len(player.list_card) > 0:
        card = player.list_card[0]
        action = Action(card=card, color=card.color, number=card.number)
        game.apply_action(action)
        # game.apply_action({"type": "play", "card": card})
        new_state = game.get_state()
        
        # Verify turn changed
        assert new_state.idx_player_active == (1 % state.cnt_player)

def test_reverse_card():
    """Test the effect of reverse cards"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    initial_direction = state.direction
    reverse_card = Card(color='red', number=None, symbol='reverse')
    
    # Simulate playing reverse card
    current_player = state.list_player[state.idx_player_active or 0]
    current_player.list_card.append(reverse_card)
    action = Action(card=reverse_card, color=reverse_card.color, number = reverse_card.number)
    game.apply_action(action)
    # game.apply_action({"type": "play", "card": reverse_card})
    new_state = game.get_state()
    
    assert new_state.direction == -initial_direction

def test_skip_card():
    """Test the effect of skip cards"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    initial_player = state.idx_player_active
    skip_card = Card(color='red', number=None, symbol='skip')
    
    # Simulate playing skip card
    current_player = state.list_player[state.idx_player_active or 0]
    current_player.list_card.append(skip_card)
    action = Action(card=skip_card, symbol=skip_card.symbol, color=skip_card.color)
    game.apply_action(action)
    # game.apply_action({"type": "play", "card": skip_card})
    new_state = game.get_state()
    
    # Should skip one player
    expected_player = (initial_player + 2) % state.cnt_player
    assert new_state.idx_player_active == expected_player

def test_draw_cards():
    """Test drawing cards mechanism"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state = game.get_state()
    
    initial_cards = len(state.list_player[0].list_card)
    
    # Simulate drawing a card
    # game.apply_action({"type": "draw"})
    action = Action(card=None, draw=1)
    game.apply_action(action)
    new_state = game.get_state()
    
    assert len(new_state.list_player[0].list_card) == initial_cards + 1 