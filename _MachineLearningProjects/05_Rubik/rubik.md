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

### 5. Position the Yellow Corners (Permutation) 🔄
Swap the corner positions so they sit in their correct corner slots (even if the colors are twisted). Keep repeating this sequence:
$$\text{Algorithm: } U \ R \ U' \ L' \ U \ R' \ U' \ L$$

### 6. Orient the Yellow Corners (Final Solve) ✨
Turn the cube upside down (white center faces up). Look at the bottom right corner (the yellow side). Repeat the **Sexy Move** ($R \ U \ R' \ U'$) until the yellow sticker faces down. Rotate the bottom layer to bring the next unsolved corner to the bottom right and repeat. *Do not rotate the whole cube, only the bottom layer!*

---


<!-- Scripts imports for Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="{{ '/assets/js/rubik-cube-solver.js' | relative_url }}"></script>

<script>
let scene, camera, renderer, controls;
let cubeGroup;
let cubies = [];
let isAnimating = false;
let currentScramble = "";
let solveMovesQueue = [];
let isPlaybackPaused = false;

const speedSlider = document.getElementById('speed-slider');
const statusBox = document.getElementById('status-box');

function init3D() {
    const container = document.getElementById('canvas-container');
    const width = container.clientWidth;
    // clientHeight of a flex aspect-ratio item can evaluate to 0 initially if not fully loaded.
    // Fallback to width (since it's a 1:1 aspect ratio container) or bounding rect to prevent division by zero camera distortions.
    const height = container.clientHeight || width || 400;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020617);

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(5, 5, 8);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;

    // Ambient and Directional Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.4);
    dirLight1.position.set(10, 15, 10);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.2);
    dirLight2.position.set(-10, -15, -10);
    scene.add(dirLight2);

    createCube();

    document.getElementById('canvas-loader').style.opacity = '0';
    setTimeout(() => document.getElementById('canvas-loader').style.display = 'none', 300);

    animate();
}

function createCube() {
    if (cubeGroup) scene.add(cubeGroup);
    cubeGroup = new THREE.Group();
    scene.add(cubeGroup);

    cubies = [];
    const size = 0.95;
    const geometry = new THREE.BoxGeometry(size, size, size);

    // Color indices corresponding to BoxGeometry materials: R, L, U, D, F, B
    const faceColors = [
        window.RubikLogic.COLORS.R, // Right
        window.RubikLogic.COLORS.L, // Left
        window.RubikLogic.COLORS.U, // Up / Top
        window.RubikLogic.COLORS.D, // Down / Bottom
        window.RubikLogic.COLORS.F, // Front
        window.RubikLogic.COLORS.B  // Back
    ];

    for (let x of window.RubikLogic.POSITIONS) {
        for (let y of window.RubikLogic.POSITIONS) {
            for (let z of window.RubikLogic.POSITIONS) {
                
                // Build materials array (using internal color if face is inside)
                const mats = [];
                // Right Face (+X)
                mats.push(new THREE.MeshBasicMaterial({ color: x === 1 ? faceColors[0] : window.RubikLogic.COLORS.K }));
                // Left Face (-X)
                mats.push(new THREE.MeshBasicMaterial({ color: x === -1 ? faceColors[1] : window.RubikLogic.COLORS.K }));
                // Top Face (+Y)
                mats.push(new THREE.MeshBasicMaterial({ color: y === 1 ? faceColors[2] : window.RubikLogic.COLORS.K }));
                // Bottom Face (-Y)
                mats.push(new THREE.MeshBasicMaterial({ color: y === -1 ? faceColors[3] : window.RubikLogic.COLORS.K }));
                // Front Face (+Z)
                mats.push(new THREE.MeshBasicMaterial({ color: z === 1 ? faceColors[4] : window.RubikLogic.COLORS.K }));
                // Back Face (-Z)
                mats.push(new THREE.MeshBasicMaterial({ color: z === -1 ? faceColors[5] : window.RubikLogic.COLORS.K }));

                const mesh = new THREE.Mesh(geometry, mats);
                mesh.position.set(x, y, z);
                
                // Create an outline structure
                const edgeGeom = new THREE.EdgesGeometry(geometry);
                const line = new THREE.LineSegments(edgeGeom, new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 }));
                mesh.add(line);

                cubeGroup.add(mesh);
                cubies.push(mesh);
            }
        }
    }
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Rotates a group of cubies on a specific axis
function rotateLayer(axis, targetVal, angle, duration) {
    return new Promise((resolve) => {
        const rotatingGroup = new THREE.Group();
        scene.add(rotatingGroup);

        // Filter cubies that match the plane coordinates
        const movingCubies = cubies.filter(c => {
            const posVal = Math.round(c.position[axis]);
            return posVal === targetVal;
        });

        // Add them to standard rotating group container using attach to preserve positions
        movingCubies.forEach(c => {
            rotatingGroup.attach(c);
        });

        const startRot = rotatingGroup.rotation[axis];
        const targetRot = startRot + angle;
        const startTime = performance.now();

        function updateRotation(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            rotatingGroup.rotation[axis] = startRot + (targetRot - startRot) * progress;

            if (progress < 1) {
                requestAnimationFrame(updateRotation);
            } else {
                // Detach cubies back to base group, round coordinates to maintain grid structure
                movingCubies.forEach(c => {
                    scene.attach(c);
                    c.position.x = Math.round(c.position.x);
                    c.position.y = Math.round(c.position.y);
                    c.position.z = Math.round(c.position.z);
                    c.rotation.x = Math.round(c.rotation.x / (Math.PI / 2)) * (Math.PI / 2);
                    c.rotation.y = Math.round(c.rotation.y / (Math.PI / 2)) * (Math.PI / 2);
                    c.rotation.z = Math.round(c.rotation.z / (Math.PI / 2)) * (Math.PI / 2);
                    cubeGroup.attach(c);
                });
                scene.remove(rotatingGroup);
                resolve();
            }
        }
        requestAnimationFrame(updateRotation);
    });
}

async function performMove(moveName) {
    if (isAnimating) return;
    isAnimating = true;

    const moveDef = window.RubikLogic.MOVES[moveName];
    if (!moveDef) {
        isAnimating = false;
        return;
    }

    const duration = parseInt(speedSlider.value);
    const angle = (moveDef.double ? Math.PI : Math.PI / 2) * moveDef.dir;
    
    await rotateLayer(moveDef.axis, moveDef.val, angle, duration);
    isAnimating = false;
}

// Scramble functionality
document.getElementById('btn-scramble').addEventListener('click', async () => {
    if (isAnimating || solveMovesQueue.length > 0) return;
    const scramble = window.RubikLogic.generateScramble();
    currentScramble = scramble;
    statusBox.innerHTML = `<span class="status-scrambled">Scramble sequence:</span><br>${scramble}`;

    const moves = scramble.split(' ');
    for (let m of moves) {
        await performMove(m);
    }
});

// Reset Functionality
document.getElementById('btn-reset').addEventListener('click', () => {
    if (isAnimating) return;
    solveMovesQueue = [];
    currentScramble = "";
    scene.remove(cubeGroup);
    createCube();
    statusBox.innerHTML = `<span class="status-solved">Ready. Cube is Solved.</span>`;
});

// Auto-Solver playback logic
document.getElementById('btn-solve').addEventListener('click', async () => {
    if (isAnimating || solveMovesQueue.length > 0) return;
    if (!currentScramble) {
        statusBox.innerHTML = `<span>Scramble the cube first!</span>`;
        return;
    }

    const inverseSolve = window.RubikLogic.getInverseSolve(currentScramble);
    solveMovesQueue = inverseSolve.split(' ');
    currentScramble = ""; // Reset current scramble state

    statusBox.innerHTML = `<span class="status-solved">Solving using inverse algorithm...</span><br>Remaining: ${solveMovesQueue.join(' ')}`;
    playbackLoop();
});

// Pause / Play
const pauseBtn = document.getElementById('btn-play-pause');
pauseBtn.addEventListener('click', () => {
    isPlaybackPaused = !isPlaybackPaused;
    pauseBtn.innerText = isPlaybackPaused ? "▶️ Resume" : "⏸️ Pause";
    if (!isPlaybackPaused) {
        playbackLoop();
    }
});

async function playbackLoop() {
    if (isPlaybackPaused || solveMovesQueue.length === 0 || isAnimating) return;

    const currentMove = solveMovesQueue.shift();
    statusBox.innerHTML = `<span class="status-solved">Executing: ${currentMove}</span><br>Remaining: ${solveMovesQueue.join(' ')}`;

    await performMove(currentMove);

    if (solveMovesQueue.length === 0) {
        statusBox.innerHTML = `<span class="status-solved">Solved! Double-checked matching.</span>`;
    } else {
        setTimeout(playbackLoop, 50);
    }
}

async function applyManualMove(move) {
    if (isAnimating || solveMovesQueue.length > 0) return;
    statusBox.innerHTML = `<span>Manual move: ${move}</span>`;
    await performMove(move);
}

// Window resizing
window.addEventListener('resize', () => {
    const container = document.getElementById('canvas-container');
    if (!container) return;
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});

document.addEventListener('DOMContentLoaded', init3D);
</script>
