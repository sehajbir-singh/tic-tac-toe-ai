# tests/test_game_logic.py
import game_logic

def test_new_board_is_empty():
    b = game_logic.new_board()
    assert len(b) == 9
    assert all(cell == '' for cell in b)

def test_win_detection_rows():
    b = game_logic.new_board()
    b[0] = b[1] = b[2] = 'X'
    assert game_logic.check_winner(b, 'X') is True
    assert game_logic.game_result(b) == 'X'

def test_draw_detection():
    # A known draw position (no winners)
    b = ['X','O','X',
         'X','O','O',
         'O','X','X']
    assert game_logic.is_board_full(b) is True
    assert game_logic.game_result(b) == 'D'

def test_best_move_blocks_win():
    # Human 'X' is about to win on next move at index 2 -> AI 'O' should block at 2
    b = ['X','X','',
         '', 'O', '',
         '', '', '']
    mv = game_logic.best_move(b, human='X', ai='O', difficulty='hard')
    # best move is 2 (block) or an equivalent best move depending on tie; assert it's a valid blocking move
    assert mv in [2]
