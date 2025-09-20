import pytest
from src.backend.game import ChessBoard

def test_initial_setup():
    game = ChessBoard()
    # Check pawns are in correct positions
    for c in range(8):
        assert game.get_piece(1, c) == "p"
        assert game.get_piece(6, c) == "P"
    # Kings in the middle
    assert game.get_piece(0, 4) == "k"
    assert game.get_piece(7, 4) == "K"

def test_legal_pawn_move():
    game = ChessBoard()
    result = game.move_piece((6, 0), (5, 0))  # White pawn one step
    assert result == ""   # no capture, should return empty string
    assert game.turn == "black"

def test_illegal_pawn_move_forward_capture():
    game = ChessBoard()
    game.move_piece((6, 0), (4, 0))  # White pawn two steps
    result = game.move_piece((1, 1), (2, 1))  # Black pawn forward (legal move)
    assert result == ""  # still legal, no capture
    # put white pawn directly in front -> illegal capture
    game.board[3][1] = "P"
    illegal = game.move_piece((2, 1), (3, 1))
    assert illegal is None  # must fail

def test_knight_jump():
    game = ChessBoard()
    result = game.move_piece((7, 1), (5, 2))  # White knight jump
    assert result == ""  # no capture
    assert game.get_piece(5, 2) == "N"


def test_rook_movement():
    game = ChessBoard()
    # Clear path for rook
    game.board[6][0] = None
    game.board[5][0] = None
    moved = game.move_piece((7, 0), (5, 0))  # white rook up
    assert moved is None
    assert game.get_piece(5, 0) == "R"

def test_checkmate_detection():
    game = ChessBoard()
    # Fool's mate setup
    game.move_piece((6, 5), (5, 5))  # f2-f3
    game.move_piece((1, 4), (3, 4))  # e7-e5
    game.move_piece((6, 6), (4, 6))  # g2-g4
    game.move_piece((0, 3), (4, 7))  # Qd8-h4 (checkmate)
    result = game.checkmate_status()
    assert "wins" in result.lower()

def test_pawn_promotion():
    game = ChessBoard()
    # Simplify board
    game.board = [[None for _ in range(8)] for _ in range(8)]
    game.board[1][0] = "P"  # white pawn ready to promote
    game.turn = "white"
    game.move_piece((1, 0), (0, 0))  # promote
    promoted = game.get_piece(0, 0)
    assert promoted in ["Q", "R", "B", "N"]  # promotion must happen
