# Rubik's Cube Reinforcement Learning Solver (Option B)

This subproject implements a 3x3x3 Rubik's Cube environment (`cube_env.py`) along with a basic Q-learning reinforcement learning agent (`solver.py`) and an interactive visualizer dashboard (`gui.py`) built with Pygame.

## Prerequisites

Ensure you have Python 3.8+ installed.

## Setup Instructions

1. Navigate to this directory:
   ```bash
   cd _MachineLearningProjects/05_Rubik/python_app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the visual application:
   ```bash
   python gui.py
   ```

## Controls & Usage

- **`S` key**: Scramble the cube randomly.
- **`A` key**: Query the AI agent to make the next move toward a solution.
- **`R` key**: Reset the cube back to the solved configuration.
- **`U`, `D`, `F`, `B`, `L`, `R`**: Perform manual rotations on the respective faces. Hold `SHIFT` to execute the counter-clockwise rotation.
