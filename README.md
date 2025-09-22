**Group 20 – Chess Game (Local 2-Player)**

**Project Overview**

This project is a chess game where two players can play locally.
Our MVP will include:

* Legal piece movement
* Turn-taking
* Detection of check and checkmate

**Team Roles**
* Group lead:
* Neala Daniel Mingyi
* Backend Team: Piece logic \& rules
 * Neala Daniel Mingyi
 * Faruk Sani Aima
 * Joshua Chukwuma Chime
 * Abdulahad Kasim Sulaiman
* UI Team: Chessboard interface
 * Chidubem Godsfavour Ogbonna
 * Caleb Olugbemi
* Pytest tests
 * Ezeani Chidiogo Scholastica
* Documentation: README, report, demo video
 * Umeakunne Silvia Adaugo
 * Joshua Chukwuma Chime

 **Project Structure**




group20-chess-game/
│
├── .github/
│   └── workflows/
│       └── tests.yml          GitHub Actions CI
│
├── src/
│   ├── backend/
│   │   └── game.py            Chess game logic
│   │
│   └── ui/
│       └── board.py           Tkinter UI
│
├── tests/
│   └── test_game.py           
│
├── demo.mp4                    Full demo video
├── demo.gif                    Short demo GIF
│
└── README.md                   Project overview




**Installation**

1\\. Clone the repository:

-  git clone <repo-link>

-  cd group20-chess-game

2\\. Install dependencies:

 - `tkinter` (comes with Python)
 - python install tk

- `pytest` (for tests)
- python install pytest



\*\*Usage\*\*

To run the game:
python -m src.ui.board
(Advisable to run on VS code)



To run tests:

pytest 


**Deliverables**

\- Local two-player chess game with Tkinter interface.

\- Demo video demonstrating gameplay. (in the repo)

\- At least two passing pytest test cases.

\- Project documentation.



**Notes**

\- Python version: 3.10.
\- The game runs locally without requiring internet access.
\- Guidance from AI was used for debugging 

