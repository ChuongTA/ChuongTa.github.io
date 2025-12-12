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

## The physic logic
The bird follows simplified Newtonia physics. It doesn't move randomly; its is acted upon **Gravity** and **Impulse**.
- Gravity: A constant downward force that accumulates every frame.
- Impulse (Flap): An instant upward force that counters gravity.
