---
title: "Flappy bird Game Part 2 🐦 with Artificial Neural Network (ANN)"
category: densys
excerpt: "In this part 2, I will explain a simple Aritifical Neural Network (ANN) model to make Flappy Bird A.I.
"
layout: single
author_profile: true
permalink: /MachineLearning/Flappy_bird_part2.md/
usemathjax: true
---

Welcome to the 2nd post in this series on coding Flappy Bird with simple ANN.

The original code was written by Max Rohowsky. You can find the instruction video in [this link](https://www.youtube.com/watch?v=zsGvCwaaMOI&pp=ygUzZmxhcHB5IGJpcmQgZGVlcCBsZWFybmluZyBmcm9tIHNjcmF0Y2ggbm8gbGlicmFyaWVz)

In this post, I will re explain it in more detail for beginners. And, I think it is also a good way to remember and understand by myself as well.

Below is the graphical abstract of the full codes with 8 different python files:

![The ML learning curve meme](images/MachineLearningMeme.jpg)  
*Fig. 1 - Project Structure and logic*

 - `main.py` imports and uses `config, components.Pipes`, and `population.Population`.
 - `config.py` imports and uses `components.Ground` to create `ground`, and holds the shared `pipes`.
 - `population.py` import `config`, `player`, and `species`; it uses `config.window` and `config.ground` when updating players, and uses `Species` to manage sepciation.
 - `player.py` imports `brain` and `config`; it uses `config.pipes` and `config.window` for vision lines and collision checks.
 - `brain.py` import `node` and `connection`; it never tocuhes `config` directly. 


There are three main steps in implementation:
•	Step 1: Building a Flappy Bird game
  •	Create an empty window
  •	Add the ground
  •	Add the pipes
  •	Add a player
  •	Implement movement, collision, and gravity
  •	Create a population of players
•	Step 2: Neural network
•	Step 3: Natural selection algorithm

Step 1: Building the Flappy Bird game
Before adding intelligence or evolution, we need a working game: a window where things move, gravity pull things down, and collisions to end the game. In step 1, we focus only on building and rendering a game, no learning yet.

1.1 The game world: window, ground, and ppipes
The "world" is a 2D space where the game happens. You need:
- Window: a 550 x 720 pixel rectangle on the screen where everything is drawn.
- Ground: a thin line at the bottom (y=500) that the bird can crash into.
- Pipes: Obstacles that scroll from right to left, with a gap the bird must pass through.

`config`: The central hub
`config` is like the "game setting" file, it holds shared objects that every module needs.

`
import components
import pygame
win_height = 720
win_width = 550
window = pygame.display.set_mode((win_width, win_height))
ground = components.Ground(win_width)
pipes = []
`
- `win_width, win_height`: screen size in pixels.​
- `window`: the actual Pygame surface you draw on every frame.​
- `ground`: a single Ground object that represents the floor.​
- `pipes`: an empty list that will hold Pipes objects as they appear.

`components.py`: defining obstacles
`components.py` defines what the world look like: the ground and pipes.
`
import pygame
import random
class Ground:
    ground_level = 500  # fixed y-position of the floor
     def __init__(self, win_width):
        self.x, self.y = 0, Ground.ground_level
        self.rect = pygame.Rect(self.x, self.y, win_width, 5)
    def draw(self, window):
        pygame.draw.rect(window, (255, 255, 255), self.rect)
`
-  `ground_level = 500`: a class variable, shared by all Ground instances. It's the y-coordinate where the ground floor exists. If the screen is 720 pixels tall, the ground sits 500 pixels down, leaving 220 pixels of sky above.
- `__init__(self, win_width)`: the width of the ground.
- `self.rect = pygame.Rect(self.x, self.y, win_width, 5)`: a rectangle is created with:
  - Top-left at `(0,500)`.
  - Width = entire window width (550 pixels).
  - Height = 5 pixels (a thin line): This rectangle is used both for drawing (a white bar) and for collision detection.
  - `draw(self, window)`: Called every frame to render the ground as a white rectangle.

 Pipes: moving obstacles
 
 `
 class Pipes:
  width = 15
  opening = 100
  def __init__(self, win_width):
      self.x = win_width
      self.bottom_height = random.randint(10, 300)
      self.top_height = Ground.ground_level - self.bottom_height - self.opening
      self.bottom_rect, self.top_rect = pygame.Rect(0, 0, 0, 0), pygame.Rect(0, 0, 0, 0)
      self.passed = False
      self.off_screen = False
  def draw(self, window):
      self.bottom_rect = pygame.Rect(
          self.x,
          Ground.ground_level - self.bottom_height,
          self.width,
          self.bottom_height
      )
      pygame.draw.rect(window, (255, 255, 255), self.bottom_rect)
      self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
      pygame.draw.rect(window, (255, 255, 255), self.top_rect)
  def update(self):
      self.x -= 1
      if self.x + Pipes.width <= 50:
          self.passed = True
      if self.x <= -self.width:
          self.off_screen = True
`
- Class variables: `width = 15` (all pupes are 15 pixels wide) and `opening = 100` (all gaps between pipes are 100 pixels tall.
- Constructor:
  - `self.x = win_width`: The pipe starts just off the right edge (at x = 550).
  - `self.bottom_height = random.randint(10,300)`: The tall of bottom_height is randomed
  - `self.top_height = Ground.ground_level - self.bottom_height - self.opening`: Define the height of the top.
So from the top of the screen down to the ground, we have: Top pipe, then a 100-pixel hole, then the bottom pipe.

- Update:
  - `self.x = -1`: moves the pupe one pixel to the left each frame, giving the sense of forward motion.
  - `if self.x + Ppipes.width <= 50`: once the right edge of the pipes passes x = 50 (roughly where the bird sits), set `passed = True`. Later, this will be used to find the "closest pipe" for the bird to see.
  - `if self.x <= - self.width`: when the entire pipe is off the left edge, set `off_screen = True`, so `main.py` can remove it.
 
