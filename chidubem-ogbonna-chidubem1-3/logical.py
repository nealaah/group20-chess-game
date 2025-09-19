import tkinter as tk
from tkinter import messagebox, simpledialog
import chess
import time

class ChessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.board = chess.Board()
        self.square_size = 80
        self.font_size = 60
        self.colors = {
            'light': '#f0d9b5',
            'dark': '#b58863',
            'highlight': '#ffff00',
            'check': '#ff0000'
        }

        # Game state variables
        self.game_active = True
        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0

        # Timer variables
        self.white_time = 300  # 5 minutes in seconds
        self.black_time = 300
        self.timer_id = None

        # Main canvas for the board
        self.canvas = tk.Canvas(self, width=8 * self.square_size, height=8 * self.square_size)
        self.canvas.pack(side=tk.LEFT)

        # Right panel for controls and info
        right_panel = tk.Frame(self)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Timer display
        self.timer_label = tk.Label(right_panel, text="White: 5:00 | Black: 5:00", font=('Arial', 14))
        self.timer_label.pack(pady=5)

        # Status and stats
        self.status = tk.Label(
            right_panel,
            text="White's turn | White wins: 0 | Black wins: 0 | Draws: 0",
            font=('Arial', 12)
        )
        self.status.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(right_panel)
        button_frame.pack(pady=10)

        self.new_game_btn = tk.Button(button_frame, text="New Game", command=self.reset_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = tk.Button(button_frame, text="Undo", command=self.undo_move)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        # Trays for captured pieces
        tray_frame = tk.Frame(right_panel)
        tray_frame.pack(pady=10)

        self.white_tray_label = tk.Label(tray_frame, text="White's Captured Pieces")
        self.white_tray_label.pack()
        self.white_tray = tk.Listbox(tray_frame, height=5, width=20, font=('Arial', 16))
        self.white_tray.pack()

        self.black_tray_label = tk.Label(tray_frame, text="Black's Captured Pieces")
        self.black_tray_label.pack(pady=(10, 0))
        self.black_tray = tk.Listbox(tray_frame, height=5, width=20, font=('Arial', 16))
        self.black_tray.pack()

        self.draw_board()
        self.pieces = {}
        self.update_pieces()

        self.selected = None
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        # Start the timer
        self.start_timer()

    # ---------------- TIMER ----------------
    def start_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.update_timer()

    def update_timer(self):
        if not self.game_active:
            return

        if self.board.turn == chess.WHITE:
            self.white_time -= 0.1
            if self.white_time <= 0:
                self.white_time = 0
                self.black_wins += 1
                self.game_over("Black wins on time!")
                return
        else:
            self.black_time -= 0.1
            if self.black_time <= 0:
                self.black_time = 0
                self.white_wins += 1
                self.game_over("White wins on time!")
                return

        white_min = int(self.white_time) // 60
        white_sec = int(self.white_time) % 60
        black_min = int(self.black_time) // 60
        black_sec = int(self.black_time) % 60

        self.timer_label.config(
            text=f"White: {white_min}:{white_sec:02d} | Black: {black_min}:{black_sec:02d}"
        )

        self.timer_id = self.after(100, self.update_timer)

    # ---------------- BOARD DRAWING ----------------
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.colors['light'] if (row + col) % 2 == 0 else self.colors['dark']
                x1 = col * self.square_size
                y1 = (7 - row) * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    tags=f"square_{chess.square(col, row)}",
                    outline=""
                )

    def update_pieces(self):
        for item in list(self.pieces.values()):
            self.canvas.delete(item)
        self.pieces.clear()
        self.clear_highlights()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col, row = chess.square_file(square), chess.square_rank(square)
                x = col * self.square_size + self.square_size // 2
                y = (7 - row) * self.square_size + self.square_size // 2
                symbol = piece.unicode_symbol()

                fill_color = 'black' if piece.color == chess.BLACK else 'white'

                item = self.canvas.create_text(
                    x, y,
                    text=symbol,
                    font=('Arial', self.font_size),
                    fill=fill_color,
                    tags=f"piece_{square}"
                )
                self.pieces[square] = item

        # Highlight the king in red if in check or checkmate
        if self.board.is_check() or self.board.is_checkmate():
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                self.highlight_square(king_square, self.colors['check'])

    def highlight_square(self, square, color):
        col, row = chess.square_file(square), chess.square_rank(square)
        x1 = col * self.square_size
        y1 = (7 - row) * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            stipple="gray50",
            tags="highlight"
        )

    def highlight_moves(self, square):
        self.clear_highlights()
        for move in self.board.legal_moves:
            if move.from_square == square:
                self.highlight_square(move.to_square, self.colors['highlight'])

    def clear_highlights(self):
        self.canvas.delete("highlight")

    # ---------------- USER INTERACTION ----------------
    def on_click(self, event):
        if not self.game_active:
            return
        square = self.get_square(event.x, event.y)
        if square is None:
            return
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected = square
            self.drag_data["item"] = self.pieces[square]
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.canvas.tag_raise(self.drag_data["item"])
            self.highlight_moves(square)

            ''' dx and dy denote the change in position of the pieces in relation to the x and y axis of the board when a move is made'''

    def on_drag(self, event):
        if not self.game_active or self.selected is None:
            return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drop(self, event):
        if not self.game_active or self.selected is None:
            return

        to_square = self.get_square(event.x, event.y)
        if to_square is None or to_square == self.selected:
            self.reset_piece_position()
            self.clear_highlights()
            self.selected = None
            return

        move = chess.Move(self.selected, to_square)

        # Pawn promotion
        piece = self.board.piece_at(self.selected)
        if (piece and piece.piece_type == chess.PAWN and
            chess.square_rank(to_square) in [0, 7]):
            promotion = self.ask_promotion()
            if promotion is None:
                self.reset_piece_position()
                self.selected = None
                self.clear_highlights()
                return
            move.promotion = promotion

        if move not in self.board.legal_moves:
            messagebox.showerror("Illegal Move", "That move is not allowed.")
            self.reset_piece_position()
            self.selected = None
            self.clear_highlights()
            return

        # Handle capture
        captured = None
        if self.board.is_capture(move):
            if self.board.is_en_passant(move):
                cap_file = chess.square_file(move.to_square)
                cap_rank = chess.square_rank(move.from_square)
                cap_square = chess.square(cap_file, cap_rank)
                captured = self.board.piece_at(cap_square)
            else:
                captured = self.board.piece_at(move.to_square)

        if captured:
            self.add_to_tray(captured, self.board.turn)

        self.board.push(move)
        self.update_pieces()
        self.clear_highlights()
        self.check_game_state()
        self.update_status()
        self.selected = None

    def reset_piece_position(self):
        col, row = chess.square_file(self.selected), chess.square_rank(self.selected)
        x = col * self.square_size + self.square_size // 2
        y = (7 - row) * self.square_size + self.square_size // 2
        self.canvas.coords(self.drag_data["item"], x, y)

    def get_square(self, x, y):
        col = x // self.square_size
        row = 7 - (y // self.square_size)
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, row)
        return None

    # ---------------- UTILITIES ----------------
    def ask_promotion(self):
        pieces = {
            "Queen": chess.QUEEN,
            "Rook": chess.ROOK,
            "Bishop": chess.BISHOP,
            "Knight": chess.KNIGHT
        }
        choice = simpledialog.askstring(
            "Promotion",
            "Choose piece: Queen, Rook, Bishop, Knight",
            parent=self
        )
        if choice and choice.capitalize() in pieces:
            return pieces[choice.capitalize()]
        return None

    def add_to_tray(self, piece, capturer_color):
        symbol = piece.unicode_symbol()
        if capturer_color == chess.WHITE:
            self.white_tray.insert(tk.END, symbol)
        else:
            self.black_tray.insert(tk.END, symbol)

    def undo_move(self):
        if not self.board.move_stack or not self.game_active:
            return

        last_move = self.board.peek()
        capturer_color = not self.board.turn

        if self.board.is_capture(last_move):
            if capturer_color == chess.WHITE:
                if self.white_tray.size() > 0:
                    self.white_tray.delete(tk.END)
            else:
                if self.black_tray.size() > 0:
                    self.black_tray.delete(tk.END)

        self.board.pop()
        self.update_pieces()
        self.clear_highlights()
        self.update_status()

    def check_game_state(self):
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            if winner == "White":
                self.white_wins += 1
            else:
                self.black_wins += 1
            self.update_pieces()
            self.game_over(f"Checkmate! {winner} wins.")
        elif self.board.is_check():
            messagebox.showwarning("Check", "Your king is in check!", parent=self)
            self.update_pieces()
        elif self.board.is_stalemate():
            self.draws += 1
            self.game_over("Stalemate! Draw.")
        elif self.board.is_insufficient_material():
            self.draws += 1
            self.game_over("Draw by insufficient material!")
        elif self.board.is_seventyfive_moves():
            self.draws += 1
            self.game_over("Draw by 75-move rule!")
        elif self.board.is_fivefold_repetition():
            self.draws += 1
            self.game_over("Draw by fivefold repetition!")

    def game_over(self, message):
        self.game_active = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        messagebox.showinfo("Game Over", message, parent=self)
        self.update_status()

    def reset_game(self):
        self.board.reset()
        self.game_active = True
        self.white_time = 300
        self.black_time = 300
        self.update_pieces()
        self.white_tray.delete(0, tk.END)
        self.black_tray.delete(0, tk.END)
        self.update_status()
        self.start_timer()

    def update_status(self):
        if not self.game_active:
            status_text = "Game Over"
        else:
            turn = "White" if self.board.turn == chess.WHITE else "Black"
            status_text = f"{turn}'s turn"
            if self.board.is_check():
                status_text += " | CHECK!"
        status_text += f" | White wins: {self.white_wins} | Black wins: {self.black_wins} | Draws: {self.draws}"
        self.status.config(text=status_text)


if __name__ == "__main__":
    app = ChessApp()
    app.mainloop()
