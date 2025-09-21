**Group 20 – Chess Game (Local 2-Player)**

**Project Overview**

This project is a chess game where two players can play locally.
Our MVP will include:

* Legal piece movement
* Turn-taking
* Detection of check and checkmate

**Team Roles**

* Backend Team: Piece logic \& rules
* UI Team: Chessboard interface
* Pytest tests \& CI
* Documentation: README, report, demo video

 **Project Structure**




group20-chess-game/
│
├── .github/
│   └── workflows/
│       └── ci.yml          
│
├── src/
│   ├── backend/
│   │   └── game.py            
│   │
│   └── ui/
│       └── board.py           
│
├── tests/
│   └── test_core.py           
│
├── demo.mp4                   
├── demo.gif                  
│
├── README.md                 



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

