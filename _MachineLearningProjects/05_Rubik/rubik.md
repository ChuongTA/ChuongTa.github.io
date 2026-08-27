---
title: "Interactive Rubik's Cube Solver & ML Explainer 🧩"
excerpt: "Learn how to solve a Rubik's Cube with interactive 3D visualizations, custom algorithms walkthrough, and Python Reinforcement Learning models."
layout: single
author_profile: true
permalink: /MachineLearningProjects/Rubik/
usemathjax: true
image: "/images/Rubik/rubik_abstract_thumbnail.jpg"
date: 2026-08-19
category: "Machine learning projects"
---

<link rel="stylesheet" href="{{ '/assets/css/rubik-style.css' | relative_url }}">

<div class="rubik-container">
    <div class="rubik-title">Rubik's Cube Simulator & Solver</div>
    
    <div class="rubik-grid">
        <!-- Interactive 3D Canvas -->
        <div class="rubik-canvas-container" id="canvas-container">
            <div class="loader-container" id="canvas-loader">
                <div class="spinner"></div>
                <div style="font-weight: 500; font-size: 0.95rem;">Initializing 3D Environment...</div>
            </div>
        </div>
        
        <!-- Controls & Panel -->
        <div class="rubik-panel">
            <div class="rubik-controls-row">
                <button class="rubik-btn" id="btn-scramble">🎲 Scramble</button>
                <button class="rubik-btn rubik-btn-accent" id="btn-solve">✨ Solve</button>
            </div>
            
            <div class="rubik-controls-row">
                <button class="rubik-btn rubik-btn-secondary" id="btn-play-pause">⏸️ Pause</button>
                <button class="rubik-btn rubik-btn-secondary" id="btn-reset">🔄 Reset</button>
            </div>

            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; display: block; margin-bottom: 6px;">
                    Rotation Speed
                </label>
                <input type="range" id="speed-slider" min="100" max="1000" value="300" style="width: 100%; accent-color: #38bdf8;">
            </div>

            <div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">Manual Moves</div>
                <div class="rubik-moves-grid">
                    <button class="rubik-move-btn" onclick="applyManualMove('R')">R</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('L')">L</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('U')">U</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('D')">D</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('F')">F</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('B')">B</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('R\'')">R'</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('L\'')">L'</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('U\'')">U'</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('D\'')">D'</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('F\'')">F'</button>
                    <button class="rubik-move-btn" onclick="applyManualMove('B\'')">B'</button>
                </div>
            </div>

            <div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">Status / Move Feed</div>
                <div class="rubik-status-box" id="status-box">
                    <span class="status-solved">Ready. Cube is Solved.</span>
                </div>
            </div>
        </div>
    </div>
</div>

## How It Works

Solving a Rubik's Cube programmatically is a classic problem in computer science. There are two primary ways algorithms solve this puzzle:
1. **Rule-Based Search (Kociemba's Algorithm)**: Solves the Rubik's cube in 20 moves or less by breaking down the $4.3 \times 10^{19}$ states into subgroups.
2. **Reinforcement Learning (RL)**: Using deep neural networks to learn representations of state orientation and using **Deep Q-Learning** or **Pathfinding with Value Iteration** to find optimal paths back to the solved state.

---

## The Python Desktop App (Option B)

If you want to train your own Reinforcement Learning Agent or run a native interactive solver on your computer, check out our Python implementation inside the `python_app` subdirectory.

To get started, clone the repository and run:
```bash
cd _MachineLearningProjects/05_Rubik/python_app
pip install -r requirements.txt
python gui.py
```

### Reinforcement Learning Implementation Details
We define the Rubik's Cube state space as a flattened vector representing color mapping of stickers.
The reward structure:
* **Solved State**: $+100$
* **Non-solved State**: $-1$ per move to encourage finding the shortest path.

Using Deep Q-Networks (DQN) or double-DQN with experience replay, the agent learns sequence behaviors to untangle the cube.

---

## 📘 Step-by-Step Guide to Solving a Rubik's Cube (Beginner's Method)

### Understanding Cube Notation 📖
To follow Rubik's Cube algorithms, you need to understand **Singmaster Notation**. Each letter represents a **$90^\circ$ clockwise rotation** of a specific face (as if you are looking directly at that face):

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 15px; margin: 20px 0; text-align: center; font-size: 0.8rem; color: #cbd5e1;">
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">U (Up)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <!-- Top perspective face -->
            <polygon points="50,15 80,30 50,45 20,30" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <path d="M50,15 L80,30 L50,45 L20,30 Z" fill="#ffffff" opacity="0.6"/>
            <!-- Arrow -->
            <path d="M 40,25 Q 50,18 60,25" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444"/>
                </marker>
            </defs>
        </svg>
        <span>Clockwise top layer</span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">D (Down)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <!-- Highlight bottom -->
            <polygon points="20,60 50,75 80,60 50,90" fill="#ffd700" opacity="0.6" stroke="#000" stroke-width="2" transform="translate(0, 5)"/>
            <path d="M 40,80 Q 50,87 60,80" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span>Clockwise bottom layer</span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">F (Front)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#009b48" opacity="0.6"/>
            <!-- Circular front arrow -->
            <path d="M 30,42 A 15,15 0 0,1 45,35" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span>Clockwise front face</span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">R (Right)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#b71234" opacity="0.6"/>
            <path d="M 62,38 L 78,50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span>Clockwise right layer</span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">L (Left)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#ff5800" opacity="0.6"/>
            <path d="M 38,62 L 22,50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span>Clockwise left layer</span>
    </div>
</div>

**Suffix Modifiers:**
*   **Prime ($'$) Suffix (e.g., $R'$, $U'$):** Rotate the face **counter-clockwise** (e.g., $R'$ is Right counter-clockwise).
*   **Number $2$ Suffix (e.g., $F2$, $U2$):** Rotate the face **$180^\circ$** (direction does not matter since two turns result in the same position).

If you want to solve the Rubik's Cube manually, here is a breakdown of the standard **Layer-by-Layer** method:

### 1. The White Cross ⬜
Find the yellow center piece. Move the 4 white edge pieces around the yellow center to form a "daisy". Then, align the non-white color of each edge with its matching center piece and rotate that layer $180^\circ$ (a double turn) down to form a clean white cross on the bottom where the white edges match their side centers.

<div class="visual-net-container">
    <div style="text-align: center; font-size: 0.8rem; color: #94a3b8; margin-right: 15px;">
        <div>Daisy Pattern Target</div>
        <div style="display: grid; grid-template-columns: repeat(3, 20px); gap: 1px; background: #020617; padding: 4px; border: 1px solid #1e293b; border-radius: 4px; margin-top: 5px;">
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#ffd700;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.8rem; color: #94a3b8;">
        <div>Bottom White Cross Target</div>
        <div style="display: grid; grid-template-columns: repeat(3, 20px); gap: 1px; background: #020617; padding: 4px; border: 1px solid #1e293b; border-radius: 4px; margin-top: 5px;">
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
            <div style="width:20px; height:20px; background:#ffffff;"></div>
            <div style="width:20px; height:20px; background:#475569;"></div>
        </div>
    </div>
</div>

### 2. The First Layer Corners 🧩
Find white corner pieces on the top layer. Position them above the slot they belong to (determined by the other two colors of the corner). Execute the key algorithm (the **Sexy Move**) until the corner is correctly placed:
$$\text{Algorithm: } R \ U \ R' \ U'$$

<div class="visual-net-container">
    <div style="text-align: center; font-size: 0.8rem; color: #94a3b8;">
        <div>Solved First Layer Target (Bottom Face + Edges match Center)</div>
        <div style="display: flex; gap: 8px; margin-top: 5px;">
            <div style="display: grid; grid-template-columns: repeat(3, 15px); gap: 1px; background: #020617; padding: 3px; border: 1px solid #1e293b; border-radius: 3px;">
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
                <div style="width:15px; height:15px; background:#ffffff;"></div>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: center; text-align: left; font-size: 0.75rem;">
                <div style="color: #10b981;">✓ Bottom layer is solid White</div>
                <div style="color: #10b981;">✓ T-shapes formed on all 4 sides</div>
            </div>
        </div>
    </div>
</div>

### 3. Middle Layer (Second Layer Edges) 🟩
Find edge pieces on the top layer that do not contain yellow. Align the front color of the edge with its matching center. 
* To insert the edge to the **Right**:
  $$\text{Algorithm: } U \ R \ U \ R' \ U' \ F' \ U' \ F$$
* To insert the edge to the **Left**:
  $$\text{Algorithm: } U' \ L' \ U' \ L \ U \ F \ U \ F'$$

### 4. Yellow Cross (Orienting Edges) 🟨
Look at the top face. You will have a dot, an 'L' shape, a horizontal line, or a cross. Repeat this algorithm to progress towards the cross:
$$\text{Algorithm: } F \ R \ U \ R' \ U' \ F'$$

<div class="visual-net-container" style="gap: 15px;">
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div>1. Dot Case</div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div>2. L-Shape Case</div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div>3. Line Case</div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div>4. Cross Target</div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
</div>

### 5. Aligning the Yellow Cross (Make a Cross Correctly with the 2nd Layer Below) 🟨
Once you have the yellow cross, you must align its side colors with the center pieces of the middle layer. 

Turn the top layer to match as many side colors to their corresponding centers as possible. 
*   **If two adjacent edges match** (e.g., Back and Right): Hold the cube so the matching edges are at the **Back** and **Right** faces, then execute the algorithm (known as **Sune**):
    $$\text{Algorithm: } R \ U \ R' \ U \ R \ U2 \ R' \ [U]$$
*   **If two opposite edges match**: Hold them on the **Left** and **Right** faces, execute the algorithm once, then re-align and follow the adjacent edges rule.

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #38bdf8;">Aligned Cross Target</div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <!-- Top Face (Yellow Cross, corners grey/unsolved) -->
            <!-- 0,0 (Grey) -->
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- 0,1 (Yellow) -->
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <!-- 0,2 (Grey) -->
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- 1,0 (Yellow) -->
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <!-- 1,1 (Center Yellow) -->
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <!-- 1,2 (Yellow) -->
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <!-- 2,0 (Grey) -->
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- 2,1 (Yellow) -->
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <!-- 2,2 (Grey) -->
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>

            <!-- Front Face (Green, corners grey) -->
            <!-- 0,0 (Grey) -->
            <polygon points="20,30 30,35 30,45 20,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- 0,1 (Green - Aligned Edge) -->
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <!-- 0,2 (Grey) -->
            <polygon points="40,40 50,45 50,55 40,50" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- Center & lower layers all Green -->
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>

            <!-- Right Face (Red, corners grey) -->
            <!-- 0,0 (Grey) -->
            <polygon points="50,45 60,40 60,50 50,55" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- 0,1 (Red - Aligned Edge) -->
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <!-- 0,2 (Grey) -->
            <polygon points="70,35 80,30 80,40 70,45" fill="#475569" stroke="#000" stroke-width="1"/>
            <!-- Center & lower layers all Red -->
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,60 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">Edges match the side centers correctly.</div>
    </div>
</div>

### 6. Orienting the Yellow Corners (Corner: Put All the Yellow Up) 🟨
Next, we orient the four corner pieces so that all their yellow stickers face upward, completing the yellow top face.

*   Hold the cube with the yellow face on top.
*   Identify an unsolved corner (yellow sticker not facing up) and move it to the **Front-Right-Top** slot by rotating only the top ($U$) layer.
*   Execute this algorithm repeatedly (usually 2 or 4 times) until the yellow sticker faces up:
    $$\text{Algorithm: } R' \ D' \ R \ D$$
*   **CRITICAL:** The bottom layers will get scrambled during this process. Do not panic and **do not rotate the whole cube**. Just rotate the top ($U$) layer to bring the next unsolved corner to the **Front-Right-Top** position, and repeat the sequence. Once all corners are yellow-up, the rest of the cube will automatically resolve itself!

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #38bdf8;">Yellow Top Face Solved</div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <!-- Top Face (All Yellow) -->
            <polygon points="50,15 60,20 50,25 40,20" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#ffd700" stroke="#000" stroke-width="1"/>

            <!-- Front Face (Green, corners mismatched colors indicating unsolved permutation) -->
            <!-- 0,0 (Red corner) -->
            <polygon points="20,30 30,35 30,45 20,40" fill="#b71234" stroke="#000" stroke-width="1"/>
            <!-- 0,1 (Green Edge) -->
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <!-- 0,2 (Orange corner) -->
            <polygon points="40,40 50,45 50,55 40,50" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <!-- Center & lower layers all Green -->
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>

            <!-- Right Face (Red, corners mismatched) -->
            <!-- 0,0 (Orange corner) -->
            <polygon points="50,45 60,40 60,50 50,55" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <!-- 0,1 (Red Edge) -->
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <!-- 0,2 (Green corner) -->
            <polygon points="70,35 80,30 80,40 70,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <!-- Center & lower layers all Red -->
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,60 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">The top face is all yellow, but corners are scrambled on the sides.</div>
    </div>
</div>

### 7. Positioning the Yellow Corners (Put the Corners Correctly) ✨
The final step is to put the yellow corners into their correct positions relative to the side faces.

*   Look for a corner piece that is in the correct slot (it aligns with the colors of its adjacent sides, even if it is rotated).
*   Hold the cube so this correct corner is at the **Front-Right-Top** slot.
*   Execute this algorithm to cycle the other three corners:
    $$\text{Algorithm: } U \ R \ U' \ L' \ U \ R' \ U' \ L$$
*   If no corners are initially in the correct slot, execute the algorithm once from any angle to position at least one corner, then repeat. Once all corners are in their correct slots, perform step 6 again if any corners need orientation, and your Rubik's cube is solved!

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">Fully Solved Cube!</div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <!-- Top Face (All Yellow) -->
            <polygon points="50,15 60,20 50,25 40,20" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#ffd700" stroke="#000" stroke-width="1"/>

            <!-- Front Face (All Green) -->
            <polygon points="20,30 30,35 30,45 20,40" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>

            <!-- Right Face (All Red) -->
            <polygon points="50,45 60,40 60,50 50,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,60 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #10b981;">All layers and sides are aligned and solved.</div>
    </div>
</div>

---


<!-- Scripts imports for Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="{{ '/assets/js/rubik-cube-solver.js' | relative_url }}"></script>

<script src="{{ '/assets/js/rubik-solver-ui.js' | relative_url }}"></script>

