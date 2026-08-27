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

<div class="lang-en" markdown="1">
Solving a Rubik's Cube programmatically is a classic problem in computer science. There are two primary ways algorithms solve this puzzle:
1. **Rule-Based Search (Kociemba's Algorithm)**: Solves the Rubik's cube in 20 moves or less by breaking down the $4.3 \times 10^{19}$ states into subgroups.
2. **Reinforcement Learning (RL)**: Using deep neural networks to learn representations of state orientation and using **Deep Q-Learning** or **Pathfinding with Value Iteration** to find optimal paths back to the solved state.
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Giải khối Rubik bằng lập trình là một bài toán kinh điển trong khoa học máy tính. Có hai phương pháp chính mà các thuật toán sử dụng để giải câu đố này:
1. **Tìm kiếm dựa trên luật lệ (Thuật toán Kociemba)**: Giải khối Rubik trong tối đa 20 bước xoay bằng cách chia nhỏ $4.3 \times 10^{19}$ trạng thái thành các nhóm con.
2. **Học Tăng Cường (Reinforcement Learning - RL)**: Sử dụng mạng nơ-ron sâu để học cách biểu diễn định hướng trạng thái và sử dụng **Deep Q-Learning** hoặc **Tìm đường với Lặp giá trị (Value Iteration)** để tìm đường đi tối ưu đưa rubik về trạng thái đã giải.
</div>

---

## The Python Desktop App (Option B)

<div class="lang-en" markdown="1">
If you want to train your own Reinforcement Learning Agent or run a native interactive solver on your computer, check out our Python implementation inside the `python_app` subdirectory.

To get started, clone the repository and run:
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Nếu bạn muốn tự huấn luyện Agent Học Tăng Cường của riêng mình hoặc chạy trình giải tương tác gốc trên máy tính, hãy xem phần triển khai mã nguồn Python của chúng tôi trong thư mục con `python_app`.

Để bắt đầu, hãy nhân bản kho lưu trữ và chạy lệnh:
</div>

```bash
cd _MachineLearningProjects/05_Rubik/python_app
pip install -r requirements.txt
python gui.py
```

### Reinforcement Learning Implementation Details

<div class="lang-en" markdown="1">
We define the Rubik's Cube state space as a flattened vector representing color mapping of stickers.
The reward structure:
* **Solved State**: $+100$
* **Non-solved State**: $-1$ per move to encourage finding the shortest path.

Using Deep Q-Networks (DQN) or double-DQN with experience replay, the agent learns sequence behaviors to untangle the cube.
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Chúng tôi định nghĩa không gian trạng thái của Rubik dưới dạng một vectơ phẳng đại diện cho bản đồ màu của các nhãn dán.
Cấu trúc phần thưởng:
* **Trạng thái Đã Giải**: $+100$
* **Trạng thái Chưa Giải**: $-1$ cho mỗi bước di chuyển để khuyến khích tìm đường đi ngắn nhất.

Sử dụng Mạng Q Sâu (DQN) hoặc double-DQN với lưu trữ trải nghiệm (experience replay), tác nhân (agent) sẽ học các hành vi chuỗi để gỡ rối khối rubik.
</div>

---

## 📘 Step-by-Step Guide to Solving a Rubik's Cube (Beginner's Method)


### Understanding Cube Notation 📖

<div class="lang-en" markdown="1">
To follow Rubik's Cube algorithms, you need to understand **Singmaster Notation**. Each letter represents a **$90^\circ$ clockwise rotation** of a specific face (as if you are looking directly at that face):
</div>
<div class="lang-vi" style="display: none;" markdown="1">
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

<div class="lang-en" markdown="1">
**Suffix Modifiers:**
*   **Prime ($'$) Suffix (e.g., $R'$, $U'$):** Rotate the face **counter-clockwise** (e.g., $R'$ is Right counter-clockwise).
*   **Number $2$ Suffix (e.g., $F2$, $U2$):** Rotate the face **$180^\circ$** (direction does not matter since two turns result in the same position).

If you want to solve the Rubik's Cube manually, here is a breakdown of the standard **Layer-by-Layer** method:
</div>
<div class="lang-vi" style="display: none;" markdown="1">
**Các Ký Hiệu Bổ Sung:**
*   **Dấu Phẩy ($'$) (ví dụ: $R'$, $U'$):** Xoay mặt đó **ngược chiều kim đồng hồ** (ví dụ: $R'$ là xoay mặt Phải ngược chiều kim).
*   **Số $2$ (ví dụ: $F2$, $U2$):** Xoay mặt đó **$180^\circ$** (hướng nào cũng được vì hai lần xoay $90^\circ$ sẽ cho kết quả giống nhau).

Nếu bạn muốn tự tay giải khối Rubik, dưới đây là chi tiết phương pháp giải từng tầng (**Layer-by-Layer**):
</div>

---

### 1. The White Cross ⬜

<div class="lang-en" markdown="1">
Find the yellow center piece. Move the 4 white edge pieces around the yellow center to form a "daisy". Then, align the non-white color of each edge with its matching center piece and rotate that layer $180^\circ$ (a double turn) down to form a clean white cross on the bottom where the white edges match their side centers.
</div>
<div class="lang-vi" style="display: none;" markdown="1">
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

<div class="lang-en" markdown="1">
Find white corner pieces on the top layer. Position them above the slot they belong to (determined by the other two colors of the corner). Execute the key algorithm (the **Sexy Move**) until the corner is correctly placed:
$$\text{Algorithm: } R \ U \ R' \ U'$$
</div>
<div class="lang-vi" style="display: none;" markdown="1">
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

<div class="lang-en" markdown="1">
Find edge pieces on the top layer that do not contain yellow. Align the front color of the edge with its matching center. 
* To insert the edge to the **Right**:
  $$\text{Algorithm: } U \ R \ U \ R' \ U' \ F' \ U' \ F$$
* To insert the edge to the **Left**:
  $$\text{Algorithm: } U' \ L' \ U' \ L \ U \ F \ U \ F'$$
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Tìm các viên cạnh ở tầng trên cùng mà không chứa màu vàng. Xoay tầng trên để màu mặt trước của viên cạnh trùng khớp với viên tâm tương ứng bên dưới.
* Để đưa viên cạnh sang khe bên **Phải**:
  $$\text{Công thức: } U \ R \ U \ R' \ U' \ F' \ U' \ F$$
* Để đưa viên cạnh sang khe bên **Trái**:
  $$\text{Công thức: } U' \ L' \ U' \ L \ U \ F \ U \ F'$$
</div>

### 4. Yellow Cross (Orienting Edges) 🟨

<div class="lang-en" markdown="1">
Look at the top face. You will have a dot, an 'L' shape, a horizontal line, or a cross. Repeat this algorithm to progress towards the cross:
$$\text{Algorithm: } F \ R \ U \ R' \ U' \ F'$$
</div>
<div class="lang-vi" style="display: none;" markdown="1">
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

<div class="lang-en" markdown="1">
Once you have the yellow cross, you must align its side colors with the center pieces of the middle layer. 

Turn the top layer to match as many side colors to their corresponding centers as possible. 
*   **If two adjacent edges match** (e.g., Back and Right): Hold the cube so the matching edges are at the **Back** and **Right** faces, then execute the algorithm (known as **Sune**):
    $$\text{Algorithm: } R \ U \ R' \ U \ R \ U2 \ R' \ [U]$$
*   **If two opposite edges match**: Hold them on the **Left** and **Right** faces, execute the algorithm once, then re-align and follow the adjacent edges rule.
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Sau khi có chữ thập vàng, bạn cần căn chỉnh màu các cạnh bên của chữ thập sao cho khớp với các viên tâm của tầng giữa (tầng 2).

Xoay tầng trên cùng để khớp nhiều cạnh nhất có thể với các tâm mặt bên tương ứng.
*   **Nếu hai cạnh liền kề khớp** (ví dụ: Mặt sau và bên Phải): Giữ khối rubik sao cho hai cạnh khớp nằm ở mặt **Sau** và mặt bên **Phải**, sau đó thực hiện công thức (gọi là **Sune**):
    $$\text{Công thức: } R \ U \ R' \ U \ R \ U2 \ R' \ [U]$$
*   **Nếu hai cạnh đối diện khớp**: Giữ chúng ở mặt bên **Trái** và mặt bên **Phải**, thực hiện công thức một lần, sau đó xoay căn chỉnh lại tầng trên và áp dụng quy tắc của hai cạnh liền kề.
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap; justify-content: center;">
    <!-- Step 5 Before -->
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #f43f5e;">
            <span class="lang-en">Before: Mismatched Edges</span>
            <span class="lang-vi" style="display: none;">Trước: Cạnh Chưa Khớp</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,45 60,40 60,50 50,55" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,50 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">Right edge (Orange) does not match center (Red).</span>
            <span class="lang-vi" style="display: none;">Cạnh bên phải (Cam) lệch so với tâm (Đỏ).</span>
        </div>
    </div>
    <!-- Step 5 After -->
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">
            <span class="lang-en">After: Aligned Cross</span>
            <span class="lang-vi" style="display: none;">Sau: Khớp Chữ Thập</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
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
            <span class="lang-en">Top face shows a solved yellow cross; side colors not yet aligned.</span>
            <span class="lang-vi" style="display: none;">Mặt trên đã có chữ thập vàng; các màu mặt bên chưa được căn chỉnh.</span>
        </div>
    </div>
    <!-- Step 5 After Edges -->
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">
            <span class="lang-en">After: Aligned Edges</span>
            <span class="lang-vi" style="display: none;">Sau: Khớp Cạnh</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,45 60,40 60,50 50,55" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,50 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">All four edge colors match their corresponding side centers.</span>
            <span class="lang-vi" style="display: none;">Cả 4 cạnh đã trùng khớp màu hoàn hảo với mặt bên.</span>
        </div>
    </div>
</div>

---

### Step 3: Position the Corners 🧩

<div class="lang-en" markdown="1">
Now, look at the yellow corners. The goal in this step is to get all four corners into their correct positions, even if they are not rotated facing the correct way (for example, a corner is in the correct spot if its three colors match the three surrounding side colors).

**Standard Formula:** $$U \ R \ U' \ L' \ U \ R' \ U' \ L$$
*   **What it means:** Top left, Right up, Top right, Left up, Top left, Right down, Top right, Left down

#### How to apply it:
*   **If zero corners are in the correct place:** Hold the cube in any rotation (with yellow on top) and perform the formula once. This will place at least one corner in the correct spot.
*   **If one corner is in the correct place:** Rotate the cube so that this correct corner is positioned in the **bottom-right of the yellow top face** (which is the Front-Right-Top / **UFR** slot). Perform the formula again. Check if all corners are in the correct place; if not, repeat the formula one more time with the correct corner still in the bottom-right.
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Bây giờ, hãy nhìn vào các góc màu vàng. Mục tiêu của bước này là đưa cả 4 viên góc về đúng vị trí (khe) của chúng, ngay cả khi chúng chưa xoay đúng mặt màu (ví dụ, một góc nằm đúng chỗ nếu 3 màu của nó khớp với 3 màu mặt tâm xung quanh).

**Công thức chuẩn:** $$U \ R \ U' \ L' \ U \ R' \ U' \ L$$
*   **Ý nghĩa:** Mặt trên sang trái, Mặt phải hướng lên, Mặt trên sang phải, Mặt trái hướng lên, Mặt trên sang trái, Mặt phải hướng xuống, Mặt trên sang phải, Mặt trái hướng xuống.

#### Cách áp dụng:
*   **Nếu không có góc nào đúng vị trí:** Giữ khối rubik ở bất kỳ hướng xoay nào (mặt vàng ở trên) và thực hiện công thức một lần. Điều này sẽ đưa ít nhất một góc về đúng chỗ.
*   **Nếu có một góc đúng vị trí:** Xoay khối rubik để viên góc đúng này nằm ở **phía dưới bên phải của mặt vàng trên cùng** (chính là góc Trước-Phải-Trên / vị trí **UFR**). Thực hiện công thức thêm lần nữa. Kiểm tra xem tất cả các góc đã về đúng vị trí chưa; nếu chưa, lặp lại công thức một lần nữa với viên góc đúng vẫn giữ ở phía dưới bên phải.
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap; justify-content: center;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #f43f5e;">
            <span class="lang-en">Before: Scrambled Corners</span>
            <span class="lang-vi" style="display: none;">Trước: Các Góc Sai Vị Trí</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,45 60,40 60,50 50,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#ff5800" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,50 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">Corners are in the wrong slots (e.g. Green face corner is Orange).</span>
            <span class="lang-vi" style="display: none;">Các viên góc nằm sai khe (ví dụ: góc ở mặt Xanh có màu Cam).</span>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">
            <span class="lang-en">After: Corners in Correct Slots</span>
            <span class="lang-vi" style="display: none;">Sau: Góc Đúng Vị Trí Khe</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,45 60,40 60,50 50,55" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,50 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">Corners belong to these slots (colors match), but are twisted.</span>
            <span class="lang-vi" style="display: none;">Các góc đã về đúng vị trí khe khớp màu, nhưng đang bị xoay lệch.</span>
        </div>
    </div>
</div>

---

### Step 4: Solve the Corners (The Core 4-Move Formula) ✨

<div class="lang-en" markdown="1">
In this final step, you will rotate the corner pieces to face the correct way, solving the entire cube. Make sure the yellow cross is still matched up and all corners are in their correct positions before starting.

**The Formula (The "Four Moves"):**
1.  Right side down ($R'$)
2.  Bottom to the left ($D'$)
3.  Right side up ($R$)
4.  Bottom to the right ($D$)

#### How to apply it:
*   **Step A:** Position one unsolved yellow corner in the **front-right spot** of the yellow top face (the **UFR** slot).
*   **Step B:** Perform the 4-move formula twice ($2\times$) and check if that corner is solved (with yellow facing up). If it is not solved, perform the 4-move formula another two times (making four times total).
*   **Step C:** **Do not rotate the entire cube.** Once the first corner is solved, rotate **only the top layer** ($U$ or $U'$) to bring the next unsolved yellow corner into that exact same front-right spot.
*   **Step D:** Repeat the 4-move formula (either 2 or 4 times) for this corner until it is solved.
*   **Step E:** Continue rotating the top layer to bring any remaining unsolved corners into the front-right spot and apply the formula until all corners are solved.

Finally, rotate the top layer to align the sides, and your Rubik's Cube is fully solved!
</div>
<div class="lang-vi" style="display: none;" markdown="1">
Trong bước cuối cùng này, bạn sẽ xoay các viên góc để hướng đúng mặt màu lên trên, hoàn thành giải toàn bộ khối rubik. Đảm bảo chữ thập màu vàng vẫn khớp màu và tất cả các viên góc đã nằm đúng vị trí khe trước khi bắt đầu.

**Công thức ("Bốn Bước Xoay"):**
1.  Mặt phải hướng xuống ($R'$)
2.  Mặt đáy sang trái ($D'$)
3.  Mặt phải hướng lên ($R$)
4.  Mặt đáy sang phải ($D$)

#### Cách áp dụng:
*   **Bước A:** Đặt một viên góc màu vàng chưa giải vào **vị trí trước-phải** của mặt vàng trên cùng (vị trí **UFR**).
*   **Bước B:** Thực hiện công thức 4 bước xoay trên 2 lần ($2\times$) và kiểm tra xem góc đó đã được giải chưa (mặt vàng hướng lên trên). Nếu chưa giải xong, thực hiện tiếp công thức 4 bước trên thêm 2 lần nữa (tổng cộng là 4 lần).
*   **Bước C:** **Tuyệt đối không xoay cả khối rubik.** Khi góc đầu tiên đã giải xong, hãy xoay **chỉ riêng tầng trên cùng** ($U$ hoặc $U'$) để đưa góc vàng chưa giải tiếp theo vào đúng vị trí trước-phải đó.
*   **Bước D:** Lặp lại công thức 4 bước xoay (2 hoặc 4 lần) cho viên góc này cho đến khi nó được giải xong.
*   **Bước E:** Tiếp tục xoay tầng trên cùng để đưa các góc chưa giải còn lại vào vị trí trước-phải và áp dụng công thức cho đến khi tất cả các góc được giải.

Cuối cùng, xoay tầng trên cùng để căn chỉnh trùng khớp các mặt bên, khối Rubik của bạn đã được giải hoàn toàn!
</div>

<div class="visual-net-container" style="gap: 20px; flex-wrap: wrap; justify-content: center;">
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #f43f5e;">
            <span class="lang-en">Before: Twisted Corners</span>
            <span class="lang-vi" style="display: none;">Trước: Các Góc Bị Xoay Lệch</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#475569" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="50,45 60,40 60,50 50,55" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,40 70,35 70,45 60,50" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,35 80,30 80,40 70,45" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,55 60,50 60,60 50,65" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,50 70,45 70,55 60,60" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,45 80,40 80,50 70,55" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="50,65 60,60 60,70 50,75" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="60,60 70,55 70,65 60,70" fill="#b71234" stroke="#000" stroke-width="1"/>
            <polygon points="70,55 80,50 80,60 70,65" fill="#b71234" stroke="#000" stroke-width="1"/>
        </svg>
        <div style="font-size: 0.75rem; margin-top: 5px; color: #a1a1aa;">
            <span class="lang-en">Corners are correct on sides, but yellow face points sideways.</span>
            <span class="lang-vi" style="display: none;">Các góc đúng khe ở mặt bên, nhưng mặt vàng hướng sang bên.</span>
        </div>
    </div>
    <div style="text-align: center; font-size: 0.85rem; color: #cbd5e1; background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); width: 220px;">
        <div style="font-weight: bold; margin-bottom: 8px; color: #10b981;">
            <span class="lang-en">After: Fully Solved!</span>
            <span class="lang-vi" style="display: none;">Sau: Giải Hoàn Tất!</span>
        </div>
        <svg width="120" height="120" viewBox="0 0 100 100">
            <polygon points="50,15 60,20 50,25 40,20" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,20 70,25 60,30 50,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="70,25 80,30 70,35 60,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,20 50,25 40,30 30,25" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,25 60,30 50,35 40,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="60,30 70,35 60,40 50,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="30,25 40,30 30,35 20,30" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="40,30 50,35 40,40 30,35" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="50,35 60,40 50,45 40,40" fill="#ffd700" stroke="#000" stroke-width="1"/>
            <polygon points="20,30 30,35 30,45 20,40" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,35 40,40 40,50 30,45" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,40 50,45 50,55 40,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,40 30,45 30,55 20,50" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,45 40,50 40,60 30,55" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,50 50,55 50,65 40,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="20,50 30,55 30,65 20,60" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="30,55 40,60 40,70 30,65" fill="#009b48" stroke="#000" stroke-width="1"/>
            <polygon points="40,60 50,65 50,75 40,70" fill="#009b48" stroke="#000" stroke-width="1"/>
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
  "Step 1: Solve the Yellow Cross 🟨": "Bước 1: Giải Chữ Thập Vàng 🟨",
  "Step 2: Match the Edges with the Side Colors 🟨": "Bước 2: Khớp Cạnh Với Màu Mặt Bên 🟨",
  "Step 3: Position the Corners 🧩": "Bước 3: Hoán Vị Góc (Đưa Góc Về Đúng Vị Trí) 🧩",
  "Step 4: Solve the Corners (The Core 4-Move Formula) ✨": "Bước 4: Giải Góc (Công Thức 4 Bước Cốt Lõi) ✨"
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
        if (window.TocSpy) window.TocSpy.refresh();
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
        if (window.TocSpy) window.TocSpy.refresh();
    }
    
    if (typeof window.updateSolverUI === 'function') {
        window.updateSolverUI();
    }
}
</script>
