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

We often treat Machine Learning libraries like TensorFlow or PyTorch as " Black bockes". We feed data in, and magic come out. However, to have better understanding on deep learning, one must understand the mathematics happening under the hood.

For this project, I set out to buld an AI **flappy bird** based on **Neuroevolution**—the process of training Neural Networks using Genetic Algorithms (Darwinian Natural Selection).

There are three main steps in this projects:
- Step 1: Building a flappy bird game
- Step 2: Neural network
- Step 3: Natural selection algorithm

For the next coming parts, I will explain detailly every step.

# Step 1: Creating a flappy bird game

Before an AI can learn, it needs a world to live in. In this step we build the "flappy bird" using the **Pygame** library. This creates the phycis, the obstacles, and the rules of survival.

## 1.1 The cordinate systems

The 1st thing to understad is the map. In mathclass, *Y goes up*. In computer graphics, *Y goes down*.
- (0,0): Top left corner of the screen.
- X increases: Moving right
- Y increases: Moving down (towards the floor).
- Y decreases: Moving up (toward the ceiling).
In the code:
`
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FLOOR_Y = 512
`
We define the boundaries. The bird must stay between `Y=0` (Ceiling) and `Y= 512` (Floor).

## 1.2 Loading images
Next task is loading images for background, floor, bird animations frames and pipes. In terms of bird animation frames, we import three main animations to make bird moving his/her wings. For the drawing pipes, we import image for drawing bottom pipe and then flip it to draw top pipe.

`# Background
background = pygame.image.load('assess/background-night.png').convert()
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
`
`# Floor
floor_img = pygame.image.load('assess/floor.png').convert()
floor_img = pygame.transform.scale(floor_img, (WINDOW_WIDTH, 100))
`
`# Bird Animation Frames
bird_down = pygame.image.load('assess/yellowbird-downflap.png').convert_alpha()
bird_mid = pygame.image.load('assess/yellowbird-midflap.png').convert_alpha()
bird_up = pygame.image.load('assess/yellowbird-upflap.png').convert_alpha()
bird_list = [bird_down, bird_mid, bird_up]
`
`# Pipes (Scaled and Flipped)
PIPE_IMG = pygame.image.load('assess/pipe-green.png').convert_alpha()
PIPE_IMG = pygame.transform.scale(PIPE_IMG, (70, 800)) # Scale tall to avoid stretching
PIPE_IMG_FLIPPED = pygame.transform.flip(PIPE_IMG, False, True) # Flip for top pipe
`
