# ♟️ Two Pawns Game AI

## 📌 Overview

This project implements an AI agent for a strategic pawn-based board game played on an 8×8 grid. The agent makes decisions using classical search algorithms and heuristic evaluation to compete against human players or other agents.

The system combines game logic, search optimization techniques, and a custom evaluation function to produce intelligent and efficient gameplay.

---

## 🧠 Key Features

* AI agent using **Minimax with Alpha-Beta pruning**
* **Iterative deepening** to handle time constraints
* **Transposition table** to cache previously evaluated states
* **Quiescence search** to avoid unstable evaluations (horizon effect)
* Play modes:

  * Human vs Human
  * Human vs AI
  * AI vs AI

---

## 🏗️ Game Representation

* The board is represented as an **8×8 2D array**

* Each cell contains:

  * `"wp"` → white pawn
  * `"bp"` → black pawn
  * `"--"` → empty

* Move generation:

  * Iterates over all pawns
  * Generates legal moves based on game rules

* Terminal states:

  * Pawn reaches last row
  * All opponent pawns captured
  * No legal moves available

---

## 🔍 Search Algorithm

The agent uses:

### Minimax + Alpha-Beta Pruning

* Explores possible game states efficiently
* Prunes branches that cannot improve the result

### Iterative Deepening

* Starts from shallow depth and increases gradually
* Ensures best move is found within time limit

### Transposition Table

* Stores previously evaluated board states
* Avoids redundant computations

👉 Effective branching factor reduced from ~4 to ~2.5

---

## 📊 Evaluation Function (Heuristic)

The AI evaluates board states using a **weighted scoring system**.

### Key Features:

* **Material advantage** (pawn difference)
* **Pawn advancement** (closer to promotion = better)
* **Passed pawns** (no blockers)
* **Captures** (reward capturing opponent pieces)
* **Hanging pawns** (penalty for vulnerable pieces)

### Example weights:

* Win: +100000
* Pawn difference: +20 per pawn
* Promotion bonus: +500
* Passed pawn: +250
* Capture: +50

👉 The agent selects moves that maximize this score.

---

## ⚡ Performance & Optimization

* Alpha-beta pruning reduces search space significantly
* Iterative deepening ensures responsiveness under time limits
* Quiescence search improves evaluation stability
* Transposition table avoids repeated calculations

---

## 🎮 How to Run

1. Start the server
2. Configure the game:

Example commands:

```text
Time 30
Setup Wa2 Wb2 Wc2 Wd2 We2 Wf2 Wg2 Wh2 Ba7 Bb7 Bc7 Bd7 Be7 Bf7 Bg7 Bh7
```

3. Choose game mode:

* `1` → Human vs Human
* `2` → Human vs Black AI
* `3` → Human vs White AI
* `4` → AI vs AI

---

## 📸 Gameplay

![Gameplay](./assets/game.gif)

---

## 💡 Key Learnings

* Designing effective heuristic functions is critical for AI performance
* Search optimization (pruning, caching) dramatically improves efficiency
* Balancing depth and computation time is essential for real-time decision making

---

## 🚀 Future Improvements

* Integrate machine learning to improve evaluation function
* Enhance move ordering for better pruning efficiency
* Improve UI and visualization of decision process

---

## 👩‍💻 Authors

* Lian Natour
* Shatha Maree
