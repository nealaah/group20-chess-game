import pytest
from src.backend.game import ChessBoard

def test_pawn_single_step():
    game = ChessBoard()
    moved = game.move_piece((6, 4), (5, 4))  # White pawn e2→e3
    assert moved == "" or moved is None
    assert game.board[5][4] == "P"
    assert game.turn == "black"

def test_knight_can_jump():
    game = ChessBoard()
    moved = game.move_piece((7, 1), (5, 2))  # White knight b1→c3
    assert moved == "" or moved is None
    assert game.board[5][2] == "N"
    assert game.turn == "black"

def test_illegal_rook_blocked():
    game = ChessBoard()
    moved = game.move_piece((7, 0), (5, 0))  # White rook a1→a3 (blocked by pawn)
    assert moved is None
    assert game.board[7][0] == "R"

def test_fools_mate_checkmate():
    game = ChessBoard()
    game.move_piece((6, 5), (5, 5))  # f2→f3
    game.move_piece((1, 4), (3, 4))  # e7→e5
    game.move_piece((6, 6), (4, 6))  # g2→g4
    game.move_piece((0, 3), (4, 7))  # Qd8→h4
    result = game.checkmate_status()
    assert result is not None
    assert "Black wins" in result
