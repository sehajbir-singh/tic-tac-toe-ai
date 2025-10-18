# gui_qt.py
"""
Tic-Tac-Toe GUI implemented with PySide6 (Qt for Python).
Uses game_logic.py for pure game rules and AI (minimax).
Run: pip install PySide6
Then: python gui_qt.py
"""



from PySide6.QtWidgets import (
    QWidget, QPushButton, QGridLayout, QVBoxLayout,
    QLabel, QHBoxLayout, QComboBox, QLineEdit, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

import game_logic

# small helper to size buttons consistently
BTN_SIZE = 110

class TicTacToeQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic-Tac-Toe (Qt)")
        self.setFixedSize(420, 560)  # small fixed window
        self.setWindowIcon(QIcon())  # replace with QIcon("assets/icon.png") if you have one

        # Model
        self.board = game_logic.new_board()
        self.human = 'X'
        self.ai = 'O'
        self.difficulty = 'hard'
        self.playing = False  # whether a game is in progress

        # UI
        self._create_controls()
        self._create_board()
        self._layout_all()
        self.update_status("Press Start to begin.")

    def _create_controls(self):
        # Top controls: name, marker, difficulty, start/reset
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Your name")

        self.marker_box = QComboBox()
        self.marker_box.addItems(["X", "O"])
        self.marker_box.setCurrentText("X")
        self.marker_box.currentTextChanged.connect(self._on_marker_change)

        self.diff_box = QComboBox()
        self.diff_box.addItems(["easy", "medium", "hard"])
        self.diff_box.setCurrentText("hard")
        self.diff_box.currentTextChanged.connect(self._on_diff_change)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_game)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_board)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFont(QFont("Arial", 11))

    def _create_board(self):
        # Create 3x3 grid of QPushButtons for board
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(8)
        self.buttons = []
        font = QFont("Arial", 28, QFont.Bold)
        for i in range(9):
            btn = QPushButton("")
            btn.setFixedSize(BTN_SIZE, BTN_SIZE)
            btn.setFont(font)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, idx=i: self.on_cell_clicked(idx))
            self.buttons.append(btn)
            self.grid_layout.addWidget(btn, i // 3, i % 3)

    def _layout_all(self):
        # top control row
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Name:"))
        top_row.addWidget(self.name_edit)
        top_row.addWidget(QLabel("Marker:"))
        top_row.addWidget(self.marker_box)
        top_row.addWidget(QLabel("Difficulty:"))
        top_row.addWidget(self.diff_box)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.reset_btn)

        main_v = QVBoxLayout(self)
        main_v.addLayout(top_row)
        main_v.addLayout(btn_row)
        main_v.addSpacing(6)
        main_v.addLayout(self.grid_layout)
        main_v.addSpacing(6)
        main_v.addWidget(self.status_label)

    # --- UI event handlers ---
    def _on_marker_change(self, text):
        self.human = text
        self.ai = 'O' if text == 'X' else 'X'
        self.update_status(f"You are {self.human}. Computer will be {self.ai}.")

    def _on_diff_change(self, text):
        self.difficulty = text
        self.update_status(f"Difficulty: {self.difficulty}")

    def start_game(self):
        self.reset_board()
        self.playing = True
        self.update_status("Game started. Your move.")

    def reset_board(self):
        self.board = game_logic.new_board()
        for b in self.buttons:
            b.setText("")
            b.setEnabled(True)
            b.setStyleSheet("")  # reset style
        self.playing = False
        self.update_status("Board reset. Press Start to play.")

    def update_status(self, text):
        self.status_label.setText(text)

    def on_cell_clicked(self, idx):
        if not self.playing:
            return
        if self.board[idx] != '':
            return
        # Apply human move
        game_logic.make_move(self.board, idx, self.human)
        self._refresh_buttons()
        if self._handle_end():  # if ended, stop
            return
        # Schedule AI move with a short delay so UI remains responsive and feels natural
        self.update_status("Computer is thinking...")
        QTimer.singleShot(200, self._ai_move)

    def _ai_move(self):
        mv = game_logic.best_move(self.board, human=self.human, ai=self.ai, difficulty=self.difficulty)
        if mv is not None:
            game_logic.make_move(self.board, mv, self.ai)
        self._refresh_buttons()
        self._handle_end()

    def _refresh_buttons(self):
        for i, mark in enumerate(self.board):
            btn = self.buttons[i]
            btn.setText(mark)
            btn.setEnabled(mark == '')

    def _handle_end(self) -> bool:
        if game_logic.check_winner(self.board, self.human):
            name = self.name_edit.text().strip() or "You"
            self.update_status(f"{name} wins! 🎉")
            QMessageBox.information(self, "Game Over", f"{name} wins!")
            self._end_game_visuals(winner=self.human)
            self.playing = False
            return True
        if game_logic.check_winner(self.board, self.ai):
            self.update_status("Computer wins!")
            QMessageBox.information(self, "Game Over", "Computer wins!")
            self._end_game_visuals(winner=self.ai)
            self.playing = False
            return True
        if game_logic.is_board_full(self.board):
            self.update_status("It's a draw!")
            QMessageBox.information(self, "Game Over", "It's a draw!")
            self.playing = False
            return True
        self.update_status("Your turn.")
        return False

    def _end_game_visuals(self, winner):
        # highlight winning line if possible
        for a,b,c in game_logic.WIN_LINES:
            if self.board[a] == self.board[b] == self.board[c] == winner:
                for i in (a,b,c):
                    self.buttons[i].setStyleSheet("background-color: #dff7e7;")
                break


