# ♟️ Chess Engine GUI - Deployment Fix

## 🐛 The Problem

Your Streamlit app works **locally** but fails on **Streamlit Cloud** with error:
```
[Errno 2] No such file or directory: 'chessV5_GUI'
```

**Why?** Your C++ executable (`chessV5_GUI.exe` or `chessV5_GUI`) exists on your local machine but **NOT** on Streamlit Cloud servers.

---

## ✅ The Solution

**Compile the C++ code ON Streamlit Cloud during deployment!**

### Step-by-Step Fix:

### 1️⃣ **Update Your GitHub Repository**

Add these 3 files to your repo:

#### **File 1: `packages.txt`** (NEW FILE!)
```
build-essential
g++
```
This tells Streamlit Cloud to install the C++ compiler.

#### **File 2: `requirements.txt`**
```
streamlit
python-chess
```

#### **File 3: `chess_gui.py`** (REPLACE YOUR CURRENT FILE)
Use the **fixed version** (`chess_gui_fixed.py`) that:
- ✅ Auto-compiles the C++ engine on first run
- ✅ Caches the compiled engine (compiles only once)
- ✅ Handles both local & cloud environments
- ✅ Shows debug info to troubleshoot

#### **File 4: `chessV5_GUI.cpp`** (MUST BE PRESENT)
Your C++ chess engine source code (you already have this).

---

### 2️⃣ **Repository Structure**

Your GitHub repo should look like this:
```
chess_engine_data_structure_course/
├── chess_gui.py              ← Replace with chess_gui_fixed.py
├── chessV5_GUI.cpp           ← Your C++ source (REQUIRED!)
├── requirements.txt          ← Python dependencies
├── packages.txt              ← NEW! System packages for compiler
└── README.md                 ← Optional
```

---

### 3️⃣ **Deploy to Streamlit Cloud**

1. Push all files to GitHub
2. Go to https://share.streamlit.io
3. Deploy your app
4. **First run:** The app will compile the C++ engine (takes ~10-30 seconds)
5. **Subsequent runs:** Uses the cached compiled engine (instant!)

---

## 🔧 How It Works

### The Magic: `@st.cache_resource` + Auto-Compilation

```python
@st.cache_resource
def compile_engine():
    """Compile C++ engine on first run"""
    cpp_file = "chessV5_GUI.cpp"
    engine_exe = "./chessV5_GUI"
    
    # Check if already compiled
    if os.path.exists(engine_exe):
        return engine_exe, None
    
    # Compile with g++
    subprocess.run(["g++", "-std=c++17", "-O2", cpp_file, "-o", engine_exe])
    
    return engine_exe, None
```

**What happens:**
1. ✅ Streamlit Cloud installs `g++` (from `packages.txt`)
2. ✅ App detects `chessV5_GUI.cpp`
3. ✅ Compiles it to `./chessV5_GUI` executable
4. ✅ Caches the result (won't recompile unless code changes)
5. ✅ Your Python code runs the compiled engine

---

## 📋 Quick Checklist

Before deploying, verify:

- [ ] `chessV5_GUI.cpp` is in your repo
- [ ] `packages.txt` exists with `build-essential` and `g++`
- [ ] `requirements.txt` has `streamlit` and `python-chess`
- [ ] `chess_gui.py` uses the fixed version (with `compile_engine()`)
- [ ] All files are committed and pushed to GitHub

---

## 🚀 Testing Locally

Test the fixed version locally:

```bash
# Install dependencies
pip install streamlit python-chess

# Run the app
streamlit run chess_gui.py
```

Click "Load Engine" and make a move (e.g., `e2e4`).

---

## 🐛 Troubleshooting

### Issue: "g++ compiler not found"
**Fix:** Make sure `packages.txt` exists with:
```
build-essential
g++
```

### Issue: "chessV5_GUI.cpp not found"
**Fix:** Make sure your C++ source file is in the repo root (same folder as `chess_gui.py`).

### Issue: Compilation errors
**Fix:** Check the Debug Info in the sidebar for compilation output. Common issues:
- Missing headers in C++ code
- Syntax errors in C++
- Wrong C++ standard (use `-std=c++17`)

### Issue: Engine still not working
1. Open the **Debug Info** expander in the sidebar
2. Check if `chessV5_GUI.cpp` is listed
3. Check if engine compiled successfully
4. Look at the engine file size (should be > 100KB)

---

## 📝 Alternative Solutions

### Option 1: Use Python Chess Library (No C++)
If you don't need the C++ engine specifically, use pure Python:
```python
import chess

# No external engine needed!
board = chess.Board()
```

### Option 2: Use Stockfish
Download Stockfish binary and use `python-chess` with it:
```python
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("stockfish")
```

### Option 3: Docker Deployment
Deploy with Docker where you have full control over the environment.

---

## 🎯 What Changed in the Fixed Version?

| **Original Code** | **Fixed Code** |
|-------------------|----------------|
| ❌ Hardcoded path to `.exe` | ✅ Auto-detects OS and compiles |
| ❌ Assumes engine exists | ✅ Compiles engine on first run |
| ❌ No error handling | ✅ Shows clear error messages |
| ❌ No debug info | ✅ Debug panel with file listing |
| ❌ Manual path input | ✅ Automatic compilation |

---

## 📞 Need Help?

If you still have issues:

1. Check the **Debug Info** section in the sidebar
2. Look at Streamlit Cloud logs for compilation errors
3. Make sure all files are in the GitHub repo
4. Verify `packages.txt` is present

---

## 🎮 How to Use

1. **Load Engine:** Click "🚀 Load Engine" (first time compiles the C++ code)
2. **Make Moves:** Enter moves in UCI format (e.g., `e2e4`, `e7e8q`)
3. **Undo/Redo:** Use the buttons in the sidebar
4. **New Game:** Reset the board anytime

---

## 📊 Performance

- **First run:** ~10-30 seconds (compilation)
- **Subsequent runs:** Instant (cached)
- **Move execution:** < 100ms

---

## ✨ Features

- ✅ Auto-compiles C++ engine on Streamlit Cloud
- ✅ Visual chess board with python-chess
- ✅ Move history tracking
- ✅ Undo/Redo functionality
- ✅ Legal move validation
- ✅ Game status detection (check, checkmate, stalemate)
- ✅ Debug panel for troubleshooting

---

**Made with ❤️ | C++ Chess Engine + Streamlit**
