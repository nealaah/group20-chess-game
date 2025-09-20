from typing import List, Tuple, Optional

class ChessBoard:
    def __init__(self):
        self.board = self._create_starting_board()
        self.turn = "white"
        self.en_passant = None       # square for en passant (row,col) or None
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}  # rights for both sides

    def _create_starting_board(self) -> List[List[str]]:
        return [
            ["r","n","b","q","k","b","n","r"],
            ["p","p","p","p","p","p","p","p"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["P","P","P","P","P","P","P","P"],
            ["R","N","B","Q","K","B","N","R"]
        ]

    def get_piece(self, row: int, col: int) -> str:
        return self.board[row][col]

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int], promotion: Optional[str] = None) -> Optional[str]:
        """Attempt to move a piece. Returns captured piece if success, None if illegal."""
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]

        if not piece or not self._is_correct_turn(piece):
            return None
        if not self._is_legal_move(piece, start, end):
            return None

        captured = self.board[er][ec]
        # Special: en passant capture
        if piece in ["P","p"] and (er,ec) == self.en_passant:
            if piece == "P":
                captured = "p"
                self.board[er+1][ec] = ""  # remove black pawn
            else:
                captured = "P"
                self.board[er-1][ec] = ""  # remove white pawn

        # Save current en passant
        prev_ep = self.en_passant
        self.en_passant = None

        self.board[er][ec] = piece
        self.board[sr][sc] = ""

        # Pawn double move → set en passant
        if piece == "P" and sr == 6 and er == 4:
            self.en_passant = (5, sc)
        if piece == "p" and sr == 1 and er == 3:
            self.en_passant = (2, sc)

        # Castling
        if piece in ["K","k"] and abs(ec - sc) == 2:
            if ec == 6:  # kingside
                self.board[er][5] = self.board[er][7]
                self.board[er][7] = ""
            elif ec == 2:  # queenside
                self.board[er][3] = self.board[er][0]
                self.board[er][0] = ""

        # Promotion
        if piece == "P" and er == 0:
            self.board[er][ec] = promotion.upper() if promotion else "Q"
        elif piece == "p" and er == 7:
            self.board[er][ec] = promotion.lower() if promotion else "q"

        # Illegal if still in check → undo
        if self.is_in_check(self.turn):
            # undo move
            self.board[sr][sc] = piece
            self.board[er][ec] = captured
            if piece in ["K","k"] and abs(ec - sc) == 2:
                if ec == 6:  # kingside
                    self.board[er][7] = self.board[er][5]; self.board[er][5] = ""
                else:
                    self.board[er][0] = self.board[er][3]; self.board[er][3] = ""
            self.en_passant = prev_ep
            return None

        # Update castling rights
        if piece == "K": self.castling_rights["K"] = self.castling_rights["Q"] = False
        if piece == "k": self.castling_rights["k"] = self.castling_rights["q"] = False
        if piece == "R":
            if sr==7 and sc==0: self.castling_rights["Q"] = False
            if sr==7 and sc==7: self.castling_rights["K"] = False
        if piece == "r":
            if sr==0 and sc==0: self.castling_rights["q"] = False
            if sr==0 and sc==7: self.castling_rights["k"] = False

        self._switch_turn()
        return captured

    # ---------------- TURN CONTROL ----------------
    def _is_correct_turn(self, piece: str) -> bool:
        return (piece.isupper() and self.turn == "white") or (piece.islower() and self.turn == "black")

    def _switch_turn(self):
        self.turn = "black" if self.turn == "white" else "white"

    # ---------------- MOVE VALIDATION ----------------
    def _is_clear_path(self, sr, sc, er, ec):
        dr = (er - sr) and ((er - sr)//abs(er-sr))
        dc = (ec - sc) and ((ec - sc)//abs(ec-sc))
        r, c = sr+dr, sc+dc
        while (r,c) != (er,ec):
            if self.board[r][c]:
                return False
            r += dr; c += dc
        return True

    def _is_legal_move(self, piece: str, start: Tuple[int,int], end: Tuple[int,int]) -> bool:
        sr, sc = start
        er, ec = end
        dr, dc = er - sr, ec - sc

        target = self.board[er][ec]
        if target and target.isupper() == piece.isupper():
            return False

        if piece in ["P","p"]:
            direction = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1
            # normal move
            if dc==0 and dr==direction and not target:
                return True
            # double move
            if dc==0 and dr==2*direction and sr==start_row and not target and not self.board[sr+direction][sc]:
                return True
            # capture
            if abs(dc)==1 and dr==direction and target:
                return True
            # en passant
            if abs(dc)==1 and dr==direction and (er,ec)==self.en_passant:
                return True
            return False

        if piece in ["R","r"]:
            return (sr==er or sc==ec) and self._is_clear_path(sr,sc,er,ec)
        if piece in ["B","b"]:
            return abs(dr)==abs(dc) and self._is_clear_path(sr,sc,er,ec)
        if piece in ["Q","q"]:
            return (sr==er or sc==ec or abs(dr)==abs(dc)) and self._is_clear_path(sr,sc,er,ec)
        if piece in ["N","n"]:
            return (abs(dr),abs(dc)) in [(2,1),(1,2)]
        if piece in ["K","k"]:
            if max(abs(dr),abs(dc))==1: return True
            # castling
            if sr==er and abs(dc)==2:
                side = "K" if piece=="K" else "k" if dc>0 else "Q" if piece=="K" else "q"
                if not self.castling_rights.get(side): return False
                if dc>0:  # kingside
                    if self.board[sr][sc+1] or self.board[sr][sc+2]: return False
                else:     # queenside
                    if self.board[sr][sc-1] or self.board[sr][sc-2] or self.board[sr][sc-3]: return False
                return not self.is_in_check(self.turn)
        return False

    # ---------------- CHECK & CHECKMATE ----------------
    def find_king(self, color: str) -> Optional[Tuple[int,int]]:
        king = "K" if color == "white" else "k"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    return (r,c)
        return None

    def is_in_check(self, color: str) -> bool:
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and ((piece.isupper() and color=="black") or (piece.islower() and color=="white")):
                    if self._is_legal_move(piece,(r,c),king_pos):
                        return True
        return False

    def has_legal_moves(self, color: str) -> bool:
        return bool(self.get_legal_moves(color))

    def checkmate_status(self) -> Optional[str]:
        if self.is_in_check(self.turn) and not self.has_legal_moves(self.turn):
            return f"Checkmate! { 'White' if self.turn=='black' else 'Black' } wins."
        elif not self.is_in_check(self.turn) and not self.has_legal_moves(self.turn):
            return "Stalemate! It's a draw."
        return None

    # ---------------- HINT SUPPORT ----------------
    def get_legal_moves(self, color: str):
        moves = []
        for sr in range(8):
            for sc in range(8):
                piece = self.board[sr][sc]
                if not piece: continue
                if (piece.isupper() and color=="white") or (piece.islower() and color=="black"):
                    for er in range(8):
                        for ec in range(8):
                            if self._is_legal_move(piece,(sr,sc),(er,ec)):
                                captured = self.board[er][ec]
                                self.board[er][ec] = piece
                                self.board[sr][sc] = ""
                                in_check = self.is_in_check(color)
                                self.board[sr][sc] = piece
                                self.board[er][ec] = captured
                                if not in_check:
                                    moves.append(((sr,sc),(er,ec)))
        return moves

    # ---------------- DEBUG ----------------
    def display(self):
        for row in self.board:
            print(" ".join(p if p else "." for p in row))
        print(f"Turn: {self.turn}")
