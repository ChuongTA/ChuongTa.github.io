# Environment Setup & Solver Installation Guide

This guide describes how to install the required Python packages and setup the GLPK solver on a Windows computer to run the forecasting and optimization models.

---

## 1. Required Python Environment

The project requires Python 3.8+ along with the following packages:

* **`pyomo`**: Mathematical optimization modeling framework.
* **`numpy`** & **`pandas`**: Data manipulation and numerical operations.
* **`scipy`**: Scientific computing (matrix processing utilities).
* **`lightgbm`**: Light Gradient Boosting Machine for day-ahead price forecasting.
* **`matplotlib`**: Data visualization (plotting the schedules).

### Install via pip:

Open your command prompt or PowerShell and run:

```bash
pip install pyomo numpy pandas scipy lightgbm matplotlib
```

---

## 2. GLPK Solver Installation (Windows)

Pyomo is an algebraic modeling language and does not solve optimization models on its own. It requires an external solver. We use **GLPK (GNU Linear Programming Kit)**.

### Step 1: Download WinGLPK

1. Go to the official SourceForge repository: [GLPK for Windows download | SourceForge.net](https://sourceforge.net/projects/winglpk/)
2. Download the latest `.zip` file (e.g., `winglpk-4.65.zip`).

### Step 2: Extract the Package

1. Extract the downloaded `.zip` file to a permanent directory on your computer, for example:
   `C:\winglpk-4.65\`

---

## 3. Configuration Options (How to Run)

There are two ways to configure your scripts to recognize GLPK:

### Option A: Point Directly to the Executable (Recommended for Portability)

In the Python code, specify the path to `glpsol.exe` directly inside the solver constructor. This is already implemented in `bess_sizing.py` and `daily_optimization.py`:

```python
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GLPK_PATH = os.path.normpath(os.path.join(
    SCRIPT_DIR, "../00_Required_Package/winglpk-4.65/glpk-4.65/w64/glpsol.exe"
))

solver = pyo.SolverFactory('glpk', executable=GLPK_PATH)
```

### Option B: Add GLPK to Windows Environment variables (Run Globally)

If you want to run Pyomo scripts globally without specifying the path in code:

1. Open the Windows Start Menu, search for **"Edit the system environment variables"**, and click it.
2. In the System Properties window, click **"Environment Variables..."** at the bottom.
3. Under **"System variables"**, find the variable named **`Path`**, select it, and click **"Edit..."**.
4. Click **"New"** and paste the path to the folder containing `glpsol.exe` (specifically the `w64` folder for 64-bit Windows):
   `C:\winglpk-4.65\glpk-4.65\w64`
5. Click **"OK"** on all windows to save the changes.
6. Verify the installation by opening a **new** command prompt and running:

   ```cmd
   glpsol --help
   ```
   If it prints the GLPK help instructions, the solver is installed globally. You can then initialize the solver in Python simply with:
   ```python
   solver = pyo.SolverFactory('glpk')
   ```
