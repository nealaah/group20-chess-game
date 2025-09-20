import tkinter as tk
import random
from src.backend.game import ChessBoard

PIECE_UNICODE = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}

class ChessUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 20: Chess")
        self.square_size = 80

        self.game = ChessBoard()
        self.selected = None
        self.drag_item = None
        self.drag_offset = (0, 0)
        self.move_history = []
        self.hint_timer = None
        self.highlighted = []  # store highlighted squares

        # canvas (board on left)
        self.canvas = tk.Canvas(root, width=8*self.square_size, height=8*self.square_size)
        self.canvas.pack(side=tk.LEFT)

        # side panel
        side_panel = tk.Frame(self.root, bg="#221F31")
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.status = tk.Label(side_panel, text="White's turn",
                               font=("Segoe UI", 14, "bold"), fg="white", bg="#221F31")
        self.status.pack(pady=10)

        btn_frame = tk.Frame(side_panel, bg="#221f31")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🎮 New Game", command=self.new_game,
                  bg="#0FCE38", fg="white", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="↩ Undo", command=self.undo_move,
                  bg="#F44336", fg="white", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💡 Hint", command=self.show_hint,
                  bg="#255A86", fg="white", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=5)

        white_frame = tk.LabelFrame(side_panel, text="White's Captured",
                                    font=("Segoe UI", 12, "bold"), fg="white", bg="#221F31")
        white_frame.pack(pady=10, fill="x")
        self.white_tray = tk.Listbox(white_frame, height=5, width=20, font=("Segoe UI", 14))
        self.white_tray.pack()

        black_frame = tk.LabelFrame(side_panel, text="Black's Captured",
                                    font=("Segoe UI", 12, "bold"), fg="white", bg="#221F31")
        black_frame.pack(pady=10, fill="x")
        self.black_tray = tk.Listbox(black_frame, height=5, width=20, font=("Segoe UI", 14))
        self.black_tray.pack()

        self.draw_board()

        # event bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        self.start_hint_timer()

    # ---------------- HINT TIMER ----------------
    def start_hint_timer(self):
        if self.hint_timer:
            self.root.after_cancel(self.hint_timer)
        self.hint_timer = self.root.after(30000, self.show_hint)  # 30s delay

    def show_hint(self):
        moves = self.game.get_legal_moves(self.game.turn)
        if moves:
            start, end = random.choice(moves)
            self.flash_hint(start[0], start[1], "blue")
            self.flash_hint(end[0], end[1], "blue")
        self.start_hint_timer()

    def flash_hint(self, row, col, color):
        x1, y1 = col*self.square_size, row*self.square_size
        x2, y2 = x1+self.square_size, y1+self.square_size
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, stipple="gray50", tags="hint")
        self.root.after(1000, lambda: self.canvas.delete(rect))

    # ---------------- BOARD ----------------
    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#EEEED2", "#686096"]

        for r in range(8):
            for c in range(8):
                x1, y1 = c*self.square_size, r*self.square_size
                x2, y2 = x1+self.square_size, y1+self.square_size
                color = colors[(r+c) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        # draw pieces
        for r in range(8):
            for c in range(8):
                piece = self.game.get_piece(r, c)
                if piece:
                    x = c*self.square_size + self.square_size/2
                    y = r*self.square_size + self.square_size/2
                    self.canvas.create_text(x, y,
                                            text=PIECE_UNICODE[piece],
                                            font=("Segoe UI Symbol", 40),
                                            tags=f"piece_{r}_{c}")

        # redraw highlighted moves (drawn on top of squares but under dragged piece when lifted)
        for (row, col) in self.highlighted:
            x1, y1 = col*self.square_size, row*self.square_size
            x2, y2 = x1+self.square_size, y1+self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3, tags="highlight")

    def get_square(self, x, y):
        col = x // self.square_size
        row = y // self.square_size
        return (row, col) if 0 <= row < 8 and 0 <= col < 8 else None

    def flash_illegal_move(self, row, col):
        x1, y1 = col*self.square_size, row*self.square_size
        x2, y2 = x1+self.square_size, y1+self.square_size
        tag = f"flash_{row}_{col}"
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", stipple="gray50", tags=tag)
        self.root.after(400, lambda: self.canvas.delete(tag))

    # ---------------- EVENTS ----------------
    def on_click(self, event):
        pos = self.get_square(event.x, event.y)
        if not pos:
            # click outside board -> clear selection/highlights
            self.selected = None
            self.drag_item = None
            self.highlighted = []
            self.draw_board()
            return

        row, col = pos
        piece = self.game.get_piece(row, col)

        if piece and ((piece.isupper() and self.game.turn=="white") or (piece.islower() and self.game.turn=="black")):
            self.selected = (row, col)

            # compute highlights first
            self.highlighted = [end for (start, end) in self.game.get_legal_moves(self.game.turn) if start == (row, col)]

            # redraw so highlights appear
            self.draw_board()

            # now find the new canvas item for this piece and prepare drag
            ids = self.canvas.find_withtag(f"piece_{row}_{col}")
            if ids:
                self.drag_item = ids[0]
                # lift it above everything so it drags on top
                try:
                    self.canvas.lift(self.drag_item)
                except Exception:
                    pass
                # compute offset so piece doesn't jump
                coords = self.canvas.coords(self.drag_item)
                if coords and len(coords) >= 2:
                    self.drag_offset = (coords[0] - event.x, coords[1] - event.y)
                else:
                    self.drag_offset = (0,0)
            else:
                self.drag_item = None
                self.drag_offset = (0,0)
        else:
            # clicked empty square or opponent piece -> deselect
            self.selected = None
            self.drag_item = None
            self.highlighted = []
            self.draw_board()

    def on_drag(self, event):
        # move piece with mouse while keeping offset
        if self.drag_item:
            ox, oy = self.drag_offset
            self.canvas.coords(self.drag_item, event.x + ox, event.y + oy)

    def on_drop(self, event):
        if not self.selected:
            self.drag_item = None
            return

        target = self.get_square(event.x, event.y)
        sr, sc = self.selected

        if target:
            captured = self.game.move_piece(self.selected, target)
            if captured is not None or captured == "":
                # valid move
                self.move_history.append((self.selected, target, captured))
                if captured:
                    if captured.isupper():
                        self.white_tray.insert(tk.END, PIECE_UNICODE[captured])
                    else:
                        self.black_tray.insert(tk.END, PIECE_UNICODE[captured])
                result = self.game.checkmate_status()
                self.status.config(text=result if result else f"{self.game.turn.capitalize()}'s turn")
                self.start_hint_timer()
            else:
                # invalid move: flash start square and snap back (red flash)
                self.flash_illegal_move(sr, sc)

        # cleanup and redraw authoritative board
        self.selected = None
        self.drag_item = None
        self.drag_offset = (0,0)
        self.highlighted = []
        self.draw_board()

    # ---------------- CONTROLS ----------------
    def new_game(self):
        self.game = ChessBoard()
        self.move_history.clear()
        self.white_tray.delete(0, tk.END)
        self.black_tray.delete(0, tk.END)
        self.status.config(text="White's turn")
        self.highlighted = []
        self.draw_board()
        self.start_hint_timer()

    def undo_move(self):
        if not self.move_history:
            return
        (sr, sc), (er, ec), captured = self.move_history.pop()
        piece = self.game.get_piece(er, ec)
        # naive restore (keeps your original undo behavior)
        self.game.board[sr][sc] = piece
        self.game.board[er][ec] = captured
        self.game._switch_turn()
        if captured:
            if captured.isupper() and self.white_tray.size() > 0:
                self.white_tray.delete(tk.END)
            elif captured.islower() and self.black_tray.size() > 0:
                self.black_tray.delete(tk.END)
        self.status.config(text=f"{self.game.turn.capitalize()}'s turn")
        self.highlighted = []
        self.draw_board()
        self.start_hint_timer()


if __name__ == "__main__":
    root = tk.Tk()
    ChessUI(root)
    root.mainloop()
