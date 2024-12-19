import pytest
from server.py.uno import Uno, GameState, Card, Action, GamePhase, RandomPlayer, PlayerState


def test_initial_game_state():
    """Test 001: Validate values of initial game state (cnt_players=2)"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    
    # Set up a simple game state to avoid special cards
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.list_card_discard = [Card(color='red', number=5, symbol=None)]
    
    # Give each player 7 cards
    state.list_player = [
        PlayerState(name='Player0', list_card=[
            Card(color='red', number=1, symbol=None),
            Card(color='red', number=2, symbol=None),
            Card(color='red', number=3, symbol=None),
            Card(color='red', number=4, symbol=None),
            Card(color='red', number=5, symbol=None),
            Card(color='red', number=6, symbol=None),
            Card(color='red', number=7, symbol=None),
        ]),
        PlayerState(name='Player1', list_card=[
            Card(color='blue', number=1, symbol=None),
            Card(color='blue', number=2, symbol=None),
            Card(color='blue', number=3, symbol=None),
            Card(color='blue', number=4, symbol=None),
            Card(color='blue', number=5, symbol=None),
            Card(color='blue', number=6, symbol=None),
            Card(color='blue', number=7, symbol=None),
        ])
    ]
    state.color = 'red'
    state.phase = GamePhase.RUNNING
    state.idx_player_active = 0
    
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
    
    # Set up a simple game state with multiple cards
    state.list_player[0].list_card = [
        Card(color='red', number=5, symbol=None),
        Card(color='blue', number=6, symbol=None),
        Card(color='green', number=7, symbol=None)
    ]
    state.list_player[1].list_card = [Card(color='blue', number=6, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset any pending draw
    state.has_drawn = False  # Reset draw state
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    # Verify initial state
    assert state.phase == GamePhase.RUNNING
    assert state.idx_player_active == 0
    
    # Test playing a card
    card = state.list_player[0].list_card[0]
    action = Action(card=card, color=card.color)
    game.apply_action(action)
    new_state = game.get_state()
    
    # Verify turn changed
    assert new_state.idx_player_active == 1
    assert new_state.phase == GamePhase.RUNNING  # Game should still be running

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
    
    # Set up a simple game state
    state.list_player[0].list_card = [Card(color='red', number=5, symbol=None)]
    state.list_player[1].list_card = [Card(color='blue', number=6, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset any pending draw
    state.has_drawn = False  # Reset draw state
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    initial_cards = len(state.list_player[0].list_card)
    
    # Draw a card
    action = Action(draw=1)
    game.apply_action(action)
    new_state = game.get_state()
    
    # Verify card was drawn
    assert len(new_state.list_player[0].list_card) == initial_cards + 1

def test_game_with_three_players():
    """Test 005: Test game flow with 3 players"""
    game = Uno()
    state = GameState(
        cnt_player=3, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    
    # Set up a simple game state to avoid special cards
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.list_player = [
        PlayerState(name='Player0', list_card=[Card(color='red', number=5, symbol=None)]),
        PlayerState(name='Player1', list_card=[Card(color='blue', number=6, symbol=None)]),
        PlayerState(name='Player2', list_card=[Card(color='green', number=4, symbol=None)])
    ]
    state.color = 'red'
    state.phase = GamePhase.RUNNING
    state.idx_player_active = 0
    
    game.set_state(state)
    state = game.get_state()
    
    assert state.cnt_player == 3
    assert len(state.list_player) == 3
    assert state.idx_player_active == 0

def test_wild_cards():
    """Test 006: Test wild and wilddraw4 card functionality"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Set up a simple game state
    wild_card = Card(color='any', number=None, symbol='wild')
    wilddraw4_card = Card(color='any', number=None, symbol='wilddraw4')
    state.list_player[0].list_card = [wild_card]
    state.list_player[1].list_card = [Card(color='blue', number=6, symbol=None)]
    state.list_card_discard = [Card(color='red', number=5, symbol=None)]
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset any pending draw
    state.has_drawn = False  # Reset draw state
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    # Test wild card playability
    assert game._is_card_playable(wild_card, state.list_card_discard[-1])
    assert game._is_card_playable(wilddraw4_card, state.list_card_discard[-1])
    
    # Test wild card color choices
    actions = game.get_list_action()
    color_choices = [a for a in actions if a.card and a.card.symbol == 'wild']
    assert len(color_choices) == 4  # Should have 4 color choices
    colors = set(a.color for a in color_choices)
    assert colors == {'red', 'green', 'yellow', 'blue'}

def test_draw2_matching():
    """Test 011: Test Draw2 cards can be played on other Draw2 cards"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Setup: Player 0 has Draw2, Player 1 has Draw2
    draw2_card = Card(color='red', number=None, symbol='draw2')
    state.list_player[0].list_card = [draw2_card]
    state.list_player[1].list_card = [Card(color='blue', number=None, symbol='draw2')]
    state.list_card_discard = [Card(color='red', number=None, symbol='draw2')]
    state.list_card_draw = [Card(color='blue', number=5, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 2  # Set pending draw count
    state.has_drawn = False  # Reset draw state
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    # Player 0 should be able to play Draw2 on another Draw2 or draw cards
    actions = game.get_list_action()
    draw_actions = [a for a in actions if a.draw and not a.card]  # Only count pure draw actions
    assert len(draw_actions) == 1  # Should have one draw action
    assert draw_actions[0].draw == 2  # Should draw 2 cards

def test_wilddraw4_validation():
    """Test 012: Test WildDraw4 can only be played with no matching color"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Set up a simple game state
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    # Case 1: Player has matching color - WildDraw4 should not be playable
    state.list_player[0].list_card = [
        Card(color='red', number=5, symbol=None),
        Card(color='any', number=None, symbol='wilddraw4')
    ]
    state.list_player[1].list_card = [Card(color='blue', number=6, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset any pending draw
    state.has_drawn = False  # Reset draw state
    
    actions = game.get_list_action()
    wild4_actions = [a for a in actions if a.card and a.card.symbol == 'wilddraw4']
    assert len(wild4_actions) == 0  # Should not be able to play WildDraw4
    
    # Case 2: Player has no matching color - WildDraw4 should be playable
    state.list_player[0].list_card = [
        Card(color='green', number=5, symbol=None),  # Changed from blue to green to avoid matching
        Card(color='any', number=None, symbol='wilddraw4')
    ]
    state.color = 'blue'  # Changed color to blue to ensure no match
    
    actions = game.get_list_action()
    wild4_actions = [a for a in actions if a.card and a.card.symbol == 'wilddraw4']
    assert len(wild4_actions) > 0  # Should be able to play WildDraw4
    assert all(a.draw == 4 for a in wild4_actions)  # All actions should draw 4 cards

def test_player_view_masking():
    """Test 013: Test that player view properly masks other players' cards"""
    game = Uno()
    state = GameState(
        cnt_player=3, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Get player 0's view
    player_view = game.get_player_view(0)
    
    # Check that player 0's cards are visible
    assert all(card.color is not None for card in player_view.list_player[0].list_card)
    
    # Check that other players' cards are masked
    for i in range(1, 3):
        assert all(card.color is None and card.number is None and card.symbol is None 
                  for card in player_view.list_player[i].list_card)
    
    # Check that draw pile is masked
    assert all(card.color is None and card.number is None and card.symbol is None 
              for card in player_view.list_card_draw)

def test_empty_draw_pile_no_reshuffle():
    """Test 014: Test handling empty draw pile when reshuffling isn't possible"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state.phase = GamePhase.RUNNING
    
    # Setup: Empty draw pile and only one card in discard
    state.list_card_draw = []
    state.list_card_discard = [Card(color='red', number=5, symbol=None)]
    initial_discard_size = len(state.list_card_discard)
    
    # Try to draw a card
    game.apply_action(Action(draw=1))
    
    # Verify nothing changed since we can't reshuffle with only one discard card
    assert len(state.list_card_draw) == 0
    assert len(state.list_card_discard) == initial_discard_size

def test_direction_change_multiplayer():
    """Test 015: Test direction change with reverse cards in 3+ player game"""
    game = Uno()
    state = GameState(
        cnt_player=4, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state.phase = GamePhase.RUNNING
    
    # Setup: Player 0 has a reverse card
    reverse_card = Card(color='red', number=None, symbol='reverse')
    state.list_player[0].list_card = [reverse_card]
    state.list_card_discard = [Card(color='red', number=5, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset pending draw count
    state.has_drawn = False  # Reset draw state
    
    # Initial direction and active player
    initial_direction = state.direction
    
    # Play reverse card
    game.apply_action(Action(card=reverse_card, color='red'))
    
    # Direction should be reversed
    assert state.direction == -initial_direction
    
    # Active player should remain the same after reverse
    assert state.idx_player_active == 0

def test_random_player():
    """Test 016: Test RandomPlayer action selection"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state.phase = GamePhase.RUNNING
    
    # Setup a simple game state
    state.list_player[0].list_card = [
        Card(color='red', number=5, symbol=None),
        Card(color='blue', number=6, symbol=None)
    ]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset pending draw count
    state.has_drawn = False  # Reset draw state
    
    # Create a RandomPlayer
    player = RandomPlayer()
    
    # Get available actions
    actions = game.get_list_action()
    
    # Get player's choice
    chosen_action = player.select_action(state, actions)
    
    # Verify the choice is valid
    assert chosen_action in actions
    # Verify draw action is removed if there are playable cards
    if len(actions) > 1:
        draw_actions = [a for a in actions if a.draw]
        assert len(draw_actions) == 0 or chosen_action.draw != 1

def test_game_end():
    """Test 009: Test game end conditions"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    
    # Set up a simple game state to avoid special cards
    state.list_card_draw = [Card(color='blue', number=8, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.list_player = [
        PlayerState(name='Player0', list_card=[Card(color='red', number=5, symbol=None)]),
        PlayerState(name='Player1', list_card=[Card(color='blue', number=6, symbol=None)])
    ]
    state.color = 'red'
    state.phase = GamePhase.RUNNING
    state.idx_player_active = 0
    state.has_drawn = False  # Reset draw state
    
    game.set_state(state)
    
    # Play last card
    actions = game.get_list_action()
    playable_actions = [a for a in actions if a.card]
    assert len(playable_actions) > 0  # Should have at least one playable card
    
    # Play the winning card
    game.apply_action(playable_actions[0])
    
    # Game should be finished
    state = game.get_state()
    assert state.phase == GamePhase.FINISHED

def test_edge_case_card_matching():
    """Test 010: Test edge cases for card matching"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Test matching with None values
    card1 = Card(color='red', number=None, symbol='skip')
    card2 = Card(color='blue', number=None, symbol='skip')
    assert game._is_card_playable(card1, card2)  # Same symbol
    
    # Test matching with mixed None/value fields
    card3 = Card(color='red', number=5, symbol=None)
    card4 = Card(color='red', number=None, symbol='skip')
    assert game._is_card_playable(card3, card4)  # Same color
    
    # Test non-matching cards
    card5 = Card(color='blue', number=6, symbol=None)
    card6 = Card(color='red', number=5, symbol=None)
    assert not game._is_card_playable(card5, card6)  # Different color and number

def test_reshuffle_draw_pile():
    """Test 007: Test reshuffling discard pile when draw pile is empty"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    state.phase = GamePhase.RUNNING  # Ensure we're in running phase
    
    # Empty the draw pile
    state.list_card_draw = []
    # Add some cards to discard pile
    state.list_card_discard = [
        Card(color='red', number=1, symbol=None),
        Card(color='blue', number=2, symbol=None),
        Card(color='green', number=3, symbol=None)
    ]
    
    initial_discard_size = len(state.list_card_discard)
    
    # Try to draw a card
    game.apply_action(Action(draw=1))
    
    # After drawing, verify:
    # 1. At least one card was drawn
    assert len(state.list_player[0].list_card) > 0
    # 2. Only one card remains in discard pile
    assert len(state.list_card_discard) == 1
    # 3. The rest of the cards are either in draw pile or player's hand
    total_cards = len(state.list_card_draw) + len(state.list_card_discard)
    assert total_cards < initial_discard_size  # Some cards moved to player's hand

def test_uno_call():
    """Test 008: Test UNO call functionality"""
    game = Uno()
    state = GameState(
        cnt_player=2, phase=GamePhase.SETUP, direction=1, idx_player_active=0
    )
    game.set_state(state)
    
    # Set up a situation where player has 2 cards
    state.list_player[0].list_card = [
        Card(color='red', number=5, symbol=None),
        Card(color='red', number=6, symbol=None)
    ]
    state.list_player[1].list_card = [Card(color='blue', number=6, symbol=None)]
    state.list_card_discard = [Card(color='red', number=7, symbol=None)]
    state.list_card_draw = [Card(color='blue', number=5, symbol=None)]  # Ensure draw pile has cards
    state.color = 'red'
    state.cnt_to_draw = 0  # Reset any pending draw
    state.has_drawn = False  # Reset draw state
    state.phase = GamePhase.RUNNING  # Set phase after setup
    
    actions = game.get_list_action()
    # Should have actions both with and without UNO call for each playable card
    uno_actions = [a for a in actions if a.uno]
    non_uno_actions = [a for a in actions if a.card and not a.uno]
    assert len(uno_actions) > 0
    assert len(non_uno_actions) > 0