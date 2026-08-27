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
    <div class="rubik-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 15px;">
        <div class="rubik-title" style="margin-bottom: 0;">
            <span class="lang-en">Rubik's Cube Simulator & Solver</span>
            <span class="lang-vi" style="display: none;">Mô Phỏng & Giải Rubik's Cube</span>
        </div>
        <button class="rubik-btn rubik-btn-secondary" id="btn-lang-toggle" onclick="toggleLanguage()" style="font-size: 0.85rem; padding: 8px 16px; display: inline-flex; align-items: center; gap: 8px; border: 1px solid rgba(255,255,255,0.15);">
            🌐 <span class="lang-en">Vietnamese / Tiếng Việt</span><span class="lang-vi" style="display: none;">English / Tiếng Anh</span>
        </button>
    </div>
    
    <div class="rubik-grid">
        <!-- Interactive 3D Canvas -->
        <div class="rubik-canvas-container" id="canvas-container">
            <div class="loader-container" id="canvas-loader">
                <div class="spinner"></div>
                <div style="font-weight: 500; font-size: 0.95rem;">
                    <span class="lang-en">Initializing 3D Environment...</span>
                    <span class="lang-vi" style="display: none;">Đang khởi tạo môi trường 3D...</span>
                </div>
            </div>
        </div>
        
        <!-- Controls & Panel -->
        <div class="rubik-panel">
            <div class="rubik-controls-row">
                <button class="rubik-btn" id="btn-scramble">
                    🎲 <span class="lang-en">Scramble</span><span class="lang-vi" style="display: none;">Xáo Trộn</span>
                </button>
                <button class="rubik-btn rubik-btn-accent" id="btn-solve">
                    ✨ <span class="lang-en">Solve</span><span class="lang-vi" style="display: none;">Giải Rubik</span>
                </button>
            </div>
            
            <div class="rubik-controls-row">
                <button class="rubik-btn rubik-btn-secondary" id="btn-play-pause">
                    <span class="lang-en">⏸️ Pause</span><span class="lang-vi" style="display: none;">⏸️ Tạm Dừng</span>
                </button>
                <button class="rubik-btn rubik-btn-secondary" id="btn-reset">
                    🔄 <span class="lang-en">Reset</span><span class="lang-vi" style="display: none;">Đặt Lại</span>
                </button>
            </div>

            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; display: block; margin-bottom: 6px;">
                    <span class="lang-en">Rotation Speed</span><span class="lang-vi" style="display: none;">Tốc Độ Xoay</span>
                </label>
                <input type="range" id="speed-slider" min="100" max="1000" value="300" style="width: 100%; accent-color: #38bdf8;">
            </div>

            <div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">
                    <span class="lang-en">Manual Moves</span><span class="lang-vi" style="display: none;">Xoay Thủ Công</span>
                </div>
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
                <div style="font-size: 0.85rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px;">
                    <span class="lang-en">Status / Move Feed</span><span class="lang-vi" style="display: none;">Trạng Thái / Các Bước</span>
                </div>
                <div class="rubik-status-box" id="status-box">
                    <span class="status-solved">
                        <span class="lang-en">Ready. Cube is Solved.</span>
                        <span class="lang-vi" style="display: none;">Sẵn sàng. Rubik đã được giải.</span>
                    </span>
                </div>
            </div>
        </div>
    </div>
</div>

## How It Works

<div class="lang-en">
Solving a Rubik's Cube programmatically is a classic problem in computer science. There are two primary ways algorithms solve this puzzle:
1. **Rule-Based Search (Kociemba's Algorithm)**: Solves the Rubik's cube in 20 moves or less by breaking down the $4.3 \times 10^{19}$ states into subgroups.
2. **Reinforcement Learning (RL)**: Using deep neural networks to learn representations of state orientation and using **Deep Q-Learning** or **Pathfinding with Value Iteration** to find optimal paths back to the solved state.
</div>
<div class="lang-vi" style="display: none;">
Giải khối Rubik bằng lập trình là một bài toán kinh điển trong khoa học máy tính. Có hai phương pháp chính mà các thuật toán sử dụng để giải câu đố này:
1. **Tìm kiếm dựa trên luật lệ (Thuật toán Kociemba)**: Giải khối Rubik trong tối đa 20 bước xoay bằng cách chia nhỏ $4.3 \times 10^{19}$ trạng thái thành các nhóm con.
2. **Học Tăng Cường (Reinforcement Learning - RL)**: Sử dụng mạng nơ-ron sâu để học cách biểu diễn định hướng trạng thái và sử dụng **Deep Q-Learning** hoặc **Tìm đường với Lặp giá trị (Value Iteration)** để tìm đường đi tối ưu đưa rubik về trạng thái đã giải.
</div>

---

## The Python Desktop App (Option B)

<div class="lang-en">
If you want to train your own Reinforcement Learning Agent or run a native interactive solver on your computer, check out our Python implementation inside the `python_app` subdirectory.

To get started, clone the repository and run:
</div>
<div class="lang-vi" style="display: none;">
Nếu bạn muốn tự huấn luyện Agent Học Tăng Cường của riêng mình hoặc chạy trình giải tương tác gốc trên máy tính, hãy xem phần triển khai mã nguồn Python của chúng tôi trong thư mục con `python_app`.

Để bắt đầu, hãy nhân bản kho lưu trữ và chạy lệnh:
</div>

```bash
cd _MachineLearningProjects/05_Rubik/python_app
pip install -r requirements.txt
python gui.py
```

### Reinforcement Learning Implementation Details

<div class="lang-en">
We define the Rubik's Cube state space as a flattened vector representing color mapping of stickers.
The reward structure:
* **Solved State**: $+100$
* **Non-solved State**: $-1$ per move to encourage finding the shortest path.

Using Deep Q-Networks (DQN) or double-DQN with experience replay, the agent learns sequence behaviors to untangle the cube.
</div>
<div class="lang-vi" style="display: none;">
Chúng tôi định nghĩa không gian trạng thái của Rubik dưới dạng một vectơ phẳng đại diện cho bản đồ màu của các nhãn dán.
Cấu trúc phần thưởng:
* **Trạng thái Đã Giải**: $+100$
* **Trạng thái Chưa Giải**: $-1$ cho mỗi bước di chuyển để khuyến khích tìm đường đi ngắn nhất.

Sử dụng Mạng Q Sâu (DQN) hoặc double-DQN với lưu trữ trải nghiệm (experience replay), tác nhân (agent) sẽ học các hành vi chuỗi để gỡ rối khối rubik.
</div>

---

## 📘 Step-by-Step Guide to Solving a Rubik's Cube (Beginner's Method)


### Understanding Cube Notation 📖

<div class="lang-en">
To follow Rubik's Cube algorithms, you need to understand **Singmaster Notation**. Each letter represents a **$90^\circ$ clockwise rotation** of a specific face (as if you are looking directly at that face):
</div>
<div class="lang-vi" style="display: none;">
Để thực hiện được các công thức xoay Rubik, bạn cần hiểu **Ký hiệu Singmaster**. Mỗi chữ cái đại diện cho một lượt xoay **$90^\circ$ theo chiều kim đồng hồ** của một mặt cụ thể (như thể bạn đang nhìn thẳng vào mặt đó):
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 15px; margin: 20px 0; text-align: center; font-size: 0.8rem; color: #cbd5e1;">
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">U (Up)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <path d="M50,15 L80,30 L50,45 L20,30 Z" fill="#ffffff" opacity="0.6"/>
            <path d="M 40,25 Q 50,18 60,25" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444"/>
                </marker>
            </defs>
        </svg>
        <span><span class="lang-en">Clockwise top layer</span><span class="lang-vi" style="display: none;">Xoay mặt U theo chiều kim</span></span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">D (Down)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,60 50,75 80,60 50,90" fill="#ffd700" opacity="0.6" stroke="#000" stroke-width="2" transform="translate(0, 5)"/>
            <path d="M 40,80 Q 50,87 60,80" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span><span class="lang-en">Clockwise bottom layer</span><span class="lang-vi" style="display: none;">Xoay mặt đáy theo chiều kim</span></span>
    </div>
    <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center; justify-content: space-between;">
        <span style="font-size: 1.2rem; font-weight: bold; color: #38bdf8;">F (Front)</span>
        <svg width="60" height="60" viewBox="0 0 100 100" style="margin: 10px 0;">
            <polygon points="50,15 80,30 50,45 20,30" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#334155" stroke="#000" stroke-width="2"/>
            <polygon points="50,45 80,30 80,60 50,75" fill="#1e293b" stroke="#000" stroke-width="2"/>
            <polygon points="20,30 50,45 50,75 20,60" fill="#009b48" opacity="0.6"/>
            <path d="M 30,42 A 15,15 0 0,1 45,35" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrow)"/>
        </svg>
        <span><span class="lang-en">Clockwise front face</span><span class="lang-vi" style="display: none;">Xoay mặt trước theo chiều kim</span></span>
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
        <span><span class="lang-en">Clockwise right layer</span><span class="lang-vi" style="display: none;">Xoay mặt bên phải theo chiều kim</span></span>
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
        <span><span class="lang-en">Clockwise left layer</span><span class="lang-vi" style="display: none;">Xoay mặt bên trái theo chiều kim</span></span>
    </div>
</div>

<div class="lang-en">
**Suffix Modifiers:**
*   **Prime ($'$) Suffix (e.g., $R'$, $U'$):** Rotate the face **counter-clockwise** (e.g., $R'$ is Right counter-clockwise).
*   **Number $2$ Suffix (e.g., $F2$, $U2$):** Rotate the face **$180^\circ$** (direction does not matter since two turns result in the same position).

If you want to solve the Rubik's Cube manually, here is a breakdown of the standard **Layer-by-Layer** method:
</div>
<div class="lang-vi" style="display: none;">
**Các Ký Hiệu Bổ Sung:**
*   **Dấu Phẩy ($'$) (ví dụ: $R'$, $U'$):** Xoay mặt đó **ngược chiều kim đồng hồ** (ví dụ: $R'$ là xoay mặt Phải ngược chiều kim).
*   **Số $2$ (ví dụ: $F2$, $U2$):** Xoay mặt đó **$180^\circ$** (hướng nào cũng được vì hai lần xoay $90^\circ$ sẽ cho kết quả giống nhau).

Nếu bạn muốn tự tay giải khối Rubik, dưới đây là chi tiết phương pháp giải từng tầng (**Layer-by-Layer**):
</div>

---

### 1. The White Cross ⬜

<div class="lang-en">
Find the yellow center piece. Move the 4 white edge pieces around the yellow center to form a "daisy". Then, align the non-white color of each edge with its matching center piece and rotate that layer $180^\circ$ (a double turn) down to form a clean white cross on the bottom where the white edges match their side centers.
</div>
<div class="lang-vi" style="display: none;">
Tìm viên tâm màu vàng ở mặt trên. Di chuyển 4 viên cạnh màu trắng xung quanh viên tâm màu vàng để tạo hình hoa cúc (daisy). Tiếp theo, xoay khớp màu bên của mỗi viên cạnh trắng với viên tâm mặt bên tương ứng rồi xoay mặt đó $180^\circ$ xuống dưới để tạo thành chữ thập màu trắng chuẩn xác ở mặt đáy.
</div>

<div class="visual-net-container">
    <div style="text-align: center; font-size: 0.8rem; color: #94a3b8; margin-right: 15px;">
        <div><span class="lang-en">Daisy Pattern Target</span><span class="lang-vi" style="display: none;">Mục Tiêu Mẫu Hoa Cúc</span></div>
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
        <div><span class="lang-en">Bottom White Cross Target</span><span class="lang-vi" style="display: none;">Mục Tiêu Chữ Thập Trắng Đáy</span></div>
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

<div class="lang-en">
Find white corner pieces on the top layer. Position them above the slot they belong to (determined by the other two colors of the corner). Execute the key algorithm (the **Sexy Move**) until the corner is correctly placed:
$$\text{Algorithm: } R \ U \ R' \ U'$$
</div>
<div class="lang-vi" style="display: none;">
Tìm các viên góc có màu trắng ở tầng trên cùng. Di chuyển chúng tới vị trí ngay trên khe mà chúng thuộc về (xác định bởi hai màu còn lại của viên góc). Thực hiện công thức cốt lõi (gọi là **Sexy Move**) cho tới khi viên góc được đặt đúng chỗ:
$$\text{Công thức: } R \ U \ R' \ U'$$
</div>

<div class="visual-net-container">
    <div style="text-align: center; font-size: 0.8rem; color: #94a3b8;">
        <div><span class="lang-en">Solved First Layer Target (Bottom Face + Edges match Center)</span><span class="lang-vi" style="display: none;">Mục Tiêu Tầng Đầu Tiên (Mặt Đáy Trắng + Khớp Cạnh Mặt Bên)</span></div>
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
                <div style="color: #10b981;"><span class="lang-en">✓ Bottom layer is solid White</span><span class="lang-vi" style="display: none;">✓ Mặt đáy đã hoàn thành Trắng</span></div>
                <div style="color: #10b981;"><span class="lang-en">✓ T-shapes formed on all 4 sides</span><span class="lang-vi" style="display: none;">✓ Tạo hình chữ T ở cả 4 mặt bên</span></div>
            </div>
        </div>
    </div>
</div>

### 3. Middle Layer (Second Layer Edges) 🟩

<div class="lang-en">
Find edge pieces on the top layer that do not contain yellow. Align the front color of the edge with its matching center. 
* To insert the edge to the **Right**:
  $$\text{Algorithm: } U \ R \ U \ R' \ U' \ F' \ U' \ F$$
* To insert the edge to the **Left**:
  $$\text{Algorithm: } U' \ L' \ U' \ L \ U \ F \ U \ F'$$
</div>
<div class="lang-vi" style="display: none;">
Tìm các viên cạnh ở tầng trên cùng mà không chứa màu vàng. Xoay tầng trên để màu mặt trước của viên cạnh trùng khớp với viên tâm tương ứng bên dưới.
* Để đưa viên cạnh sang khe bên **Phải**:
  $$\text{Công thức: } U \ R \ U \ R' \ U' \ F' \ U' \ F$$
* Để đưa viên cạnh sang khe bên **Trái**:
  $$\text{Công thức: } U' \ L' \ U' \ L \ U \ F \ U \ F'$$
</div>

### 4. Yellow Cross (Orienting Edges) 🟨

<div class="lang-en">
Look at the top face. You will have a dot, an 'L' shape, a horizontal line, or a cross. Repeat this algorithm to progress towards the cross:
$$\text{Algorithm: } F \ R \ U \ R' \ U' \ F'$$
</div>
<div class="lang-vi" style="display: none;">
Nhìn vào mặt trên của khối rubik. Bạn sẽ có một trong bốn trường hợp: một chấm tròn vàng ở tâm, hình chữ 'L' ngược, một đường thẳng nằm ngang hoặc chữ thập đã hoàn thành. Lặp lại công thức dưới đây để đạt được mục tiêu chữ thập:
$$\text{Công thức: } F \ R \ U \ R' \ U' \ F'$$
</div>

<div class="visual-net-container" style="gap: 15px;">
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div><span class="lang-en">1. Dot Case</span><span class="lang-vi" style="display: none;">1. Trường hợp Chấm</span></div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div><span class="lang-en">2. L-Shape Case</span><span class="lang-vi" style="display: none;">2. Trường hợp Chữ L</span></div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div><span class="lang-en">3. Line Case</span><span class="lang-vi" style="display: none;">3. Trường hợp Đường Thẳng</span></div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
        <div><span class="lang-en">4. Cross Target</span><span class="lang-vi" style="display: none;">4. Mục Tiêu Chữ Thập</span></div>
        <div style="display: grid; grid-template-columns: repeat(3, 12px); gap: 1px; background: #020617; padding: 2px; border: 1px solid #1e293b; border-radius: 3px; margin-top: 3px;">
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
            <div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#ffd700;"></div>
            <div style="width:12px; height:12px; background:#475569;"></div><div style="width:12px; height:12px; background:#ffd700;"></div><div style="width:12px; height:12px; background:#475569;"></div>
        </div>
    </div>
</div>

### 5. Aligning the Yellow Cross (Make a Cross Correctly with the 2nd Layer Below) 🟨

<div class="lang-en">
Once you have the yellow cross, you must align its side colors with the center pieces of the middle layer. 

Turn the top layer to match as many side colors to their corresponding centers as possible. 
*   **If two adjacent edges match** (e.g., Back and Right): Hold the cube so the matching edges are at the **Back** and **Right** faces, then execute the algorithm (known as **Sune**):
    $$\text{Algorithm: } R \ U \ R' \ U \ R \ U2 \ R' \ [U]$$
*   **If two opposite edges match**: Hold them on the **Left** and **Right** faces, execute the algorithm once, then re-align and follow the adjacent edges rule.
</div>
<div class="lang-vi" style="display: none;">
Sau khi có chữ thập vàng, bạn cần căn chỉnh màu các cạnh bên của chữ thập sao cho khớp với các viên tâm của tầng giữa (tầng 2).

Xoay tầng trên cùng để khớp nhiều cạnh nhất có thể với các tâm mặt bên tương ứng.
*   **Nếu hai cạnh liền kề khớp** (ví dụ: Mặt sau và bên Phải): Giữ khối rubik sao cho hai cạnh khớp nằm ở mặt **Sau** và mặt bên **Phải**, sau đó thực hiện công thức (gọi là **Sune**):
    $$\text{Công thức: } R \ U \ R' \ U \ R \ U2 \ R' \ [U]$$
*   **Nếu hai cạnh đối diện khớp**: Giữ chúng ở mặt bên **Trái** và mặt bên **Phải**, thực hiện công thức một lần, sau đó xoay căn chỉnh lại tầng trên và áp dụng quy tắc của hai cạnh liền kề.
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #38bdf8;">
            <span class="lang-en">Aligned Cross Target</span>
            <span class="lang-vi" style="display: none;">Mục Tiêu Khớp Chữ Thập</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <!-- Top Face (Yellow Cross, corners grey/unsolved) -->
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>

            <!-- Front Face (Green, corners grey) -->
            <polygon points="20,30 30,35 30,45 20,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>

            <!-- Right Face (Red, corners grey) -->
            <polygon points="50,45 60,40 60,50 50,55" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,60 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">Edges match the side centers correctly.</span>
            <span class="lang-vi" style="display: none;">Các cạnh đã khớp đúng với tâm bên.</span>
        </div>
    </div>
</div>

### 6. Orienting the Yellow Corners (Corner: Put All the Yellow Up) 🟨

<div class="lang-en">
Next, we orient the four corner pieces so that all their yellow stickers face upward, completing the yellow top face.

*   Hold the cube with the yellow face on top.
*   Identify an unsolved corner (yellow sticker not facing up) and move it to the **Front-Right-Top** slot by rotating only the top ($U$) layer.
*   Execute this algorithm repeatedly (usually 2 or 4 times) until the yellow sticker faces up:
    $$\text{Algorithm: } R' \ D' \ R \ D$$
*   **CRITICAL:** The bottom layers will get scrambled during this process. Do not panic and **do not rotate the whole cube**. Just rotate the top ($U$) layer to bring the next unsolved corner to the **Front-Right-Top** position, and repeat the sequence. Once all corners are yellow-up, the rest of the cube will automatically resolve itself!
</div>
<div class="lang-vi" style="display: none;">
Tiếp theo, chúng ta định hướng 4 viên góc sao cho tất cả các nhãn dán màu vàng đều hướng lên trên, hoàn thành mặt màu vàng ở phía trên cùng.

*   Giữ khối rubik sao cho mặt màu vàng ở trên.
*   Xác định một góc chưa được giải (màu vàng chưa hướng lên trên) và chuyển nó về vị trí góc **Trước-Phải-Trên** bằng cách chỉ xoay duy nhất tầng trên cùng ($U$).
*   Thực hiện công thức dưới đây liên tục (thường là 2 hoặc 4 lần) cho đến khi mặt vàng hướng lên trên:
    $$\text{Công thức: } R' \ D' \ R \ D$$
*   **QUAN TRỌNG:** Tầng dưới cùng sẽ bị xáo trộn trong khi thực hiện công thức này. Đừng lo lắng và **tuyệt đối không xoay cả khối rubik**. Chỉ xoay duy nhất tầng trên ($U$) để đưa góc chưa định hướng tiếp theo vào vị trí góc **Trước-Phải-Trên**, rồi lặp lại công thức trên. Khi giải xong toàn bộ các góc, các tầng dưới sẽ tự động được xếp lại đúng chuẩn!
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #38bdf8;">
            <span class="lang-en">Yellow Top Face Solved</span>
            <span class="lang-vi" style="display: none;">Đã Hoàn Thành Mặt Vàng</span>
        </div>
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

            <!-- Front Face (Green, corners mismatched) -->
            <polygon points="20,30 30,35 30,45 20,40" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>

            <!-- Right Face (Red, corners mismatched) -->
            <polygon points="50,45 60,40 60,50 50,55" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,60 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">The top face is all yellow, but corners are scrambled on the sides.</span>
            <span class="lang-vi" style="display: none;">Mặt trên đã vàng hoàn toàn, nhưng các góc bên cạnh vẫn bị lệch.</span>
        </div>
    </div>
</div>

### 7. Positioning the Yellow Corners (Put the Corners Correctly) ✨

<div class="lang-en">
The final step is to put the yellow corners into their correct positions relative to the side faces.

*   Look for a corner piece that is in the correct slot (it aligns with the colors of its adjacent sides, even if it is rotated).
*   Hold the cube so this correct corner is at the **Front-Right-Top** slot.
*   Execute this algorithm to cycle the other three corners:
    $$\text{Algorithm: } U \ R \ U' \ L' \ U \ R' \ U' \ L$$
*   If no corners are initially in the correct slot, execute the algorithm once from any angle to position at least one corner, then repeat. Once all corners are in their correct slots, perform step 6 again if any corners need orientation, and your Rubik's cube is solved!
</div>
<div class="lang-vi" style="display: none;">
Bước cuối cùng là hoán đổi các góc màu vàng về đúng vị trí tương đối của chúng so với các mặt bên cạnh.

*   Tìm một góc đã nằm ở đúng vị trí khe của nó (nằm giữa 3 màu của các mặt bên cạnh, ngay cả khi nó đang bị xoay ngược).
*   Giữ rubik sao cho viên góc đúng này nằm ở vị trí góc **Trước-Phải-Trên**.
*   Thực hiện công thức dưới đây để hoán vị xoay vòng 3 góc còn lại:
    $$\text{Công thức: } U \ R \ U' \ L' \ U \ R' \ U' \ L$$
*   Nếu ban đầu không góc nào đúng vị trí, hãy thực hiện công thức này từ góc độ bất kỳ một lần để tạo ra ít nhất một góc đúng, rồi lặp lại các bước trên. Khi các góc đã đúng vị trí và hướng mặt vàng lên trên, khối Rubik của bạn đã hoàn thành hoàn toàn!
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">
            <span class="lang-en">Fully Solved Cube!</span>
            <span class="lang-vi" style="display: none;">Hoàn Thành Giải Rubik!</span>
        </div>
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
        <div style="font-size: 0.75rem; margin-top: 5px; color: #10b981;">
            <span class="lang-en">All layers and sides are aligned and solved.</span>
            <span class="lang-vi" style="display: none;">Toàn bộ các tầng và mặt bên đã hoàn thành!</span>
        </div>
    </div>
</div>

---


<!-- Scripts imports for Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="{{ '/assets/js/rubik-cube-solver.js' | relative_url }}"></script>

<script src="{{ '/assets/js/rubik-solver-ui.js' | relative_url }}"></script>

<script>
window.currentLanguage = 'en';

const HEADING_TRANSLATIONS = {
  "How It Works": "Nguyên Lý Hoạt Động",
  "The Python Desktop App (Option B)": "Ứng Dụng Desktop Bằng Python (Tùy chọn B)",
  "Reinforcement Learning Implementation Details": "Chi Tiết Triển Khai Học Tăng Cường",
  "Understanding Cube Notation 📖": "Tìm Hiểu Ký Hiệu Rubik 📖",
  "1. The White Cross ⬜": "1. Chữ Thập Trắng ⬜",
  "2. The First Layer Corners 🧩": "2. Giải Góc Tầng Đầu Tiên 🧩",
  "3. Middle Layer (Second Layer Edges) 🟩": "3. Tầng Giữa (Cạnh Tầng Hai) 🟩",
  "4. Yellow Cross (Orienting Edges) 🟨": "4. Chữ Thập Vàng (Định Hướng Cạnh) 🟨",
  "5. Aligning the Yellow Cross (Make a Cross Correctly with the 2nd Layer Below) 🟨": "5. Căn Chỉnh Chữ Thập Vàng (Làm Đúng Chữ Thập Với Tầng 2 Bên Dưới) 🟨",
  "6. Orienting the Yellow Corners (Corner: Put All the Yellow Up) 🟨": "6. Định Hướng Góc Vàng (Góc: Đưa Tất Cả Mặt Vàng Lên Trên) 🟨",
  "7. Positioning the Yellow Corners (Put the Corners Correctly) ✨": "7. Hoán Vị Góc Vàng (Đặt Các Góc Đúng Vị Trí) ✨"
};

const HEADING_TRANSLATIONS_REV = {};
for (const key in HEADING_TRANSLATIONS) {
  HEADING_TRANSLATIONS_REV[HEADING_TRANSLATIONS[key]] = key;
}

function translateHeadings(toLang) {
  const dict = toLang === 'vi' ? HEADING_TRANSLATIONS : HEADING_TRANSLATIONS_REV;
  
  // Translate headings
  const headings = document.querySelectorAll('h2, h3');
  headings.forEach(h => {
    const text = h.textContent.trim();
    if (dict[text]) {
      h.textContent = dict[text];
    }
  });
  
  // Translate TOC links
  const links = document.querySelectorAll('a, .toc a, .nav a');
  links.forEach(a => {
    const text = a.textContent.trim();
    if (dict[text]) {
      a.textContent = dict[text];
    }
  });
}

function toggleLanguage() {
    window.currentLanguage = window.currentLanguage === 'vi' ? 'en' : 'vi';
    const enElements = document.querySelectorAll('.lang-en');
    const viElements = document.querySelectorAll('.lang-vi');
    
    const isEn = window.currentLanguage === 'en';
    
    if (!isEn) {
        enElements.forEach(el => el.style.display = 'none');
        viElements.forEach(el => {
            if (el.tagName === 'SPAN') {
                el.style.display = 'inline';
            } else if (el.tagName === 'DIV' && el.classList.contains('visual-net-container')) {
                el.style.display = 'flex';
            } else {
                el.style.display = 'block';
            }
        });
        translateHeadings('vi');
    } else {
        enElements.forEach(el => {
            if (el.tagName === 'SPAN') {
                el.style.display = 'inline';
            } else if (el.tagName === 'DIV' && el.classList.contains('visual-net-container')) {
                el.style.display = 'flex';
            } else {
                el.style.display = 'block';
            }
        });
        viElements.forEach(el => el.style.display = 'none');
        translateHeadings('en');
    }
    
    if (typeof window.updateSolverUI === 'function') {
        window.updateSolverUI();
    }
}
</script>
