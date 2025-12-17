import streamlit as st
import subprocess
import chess
import chess.svg
import platform
import os
import sys

class CustomChessEngine:
    def __init__(self, engine_path):
        self.process = subprocess.Popen(
            engine_path, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True, 
            bufsize=1
        )
        self.read_state()
    
    def read_state(self):
        lines = []
        for _ in range(20):
            line = self.process.stdout.readline().strip()
            if line: 
                lines.append(line)
            if "STATUS" in line: 
                break
        return lines
    
    def send_move(self, move_str):
        self.process.stdin.write(f"MOVE {move_str}\n")
        self.process.stdin.flush()
        return self.read_state()
    
    def undo(self):
        self.process.stdin.write("UNDO\n")
        self.process.stdin.flush()
        return self.read_state()
    
    def redo(self):
        self.process.stdin.write("REDO\n")
        self.process.stdin.flush()
        return self.read_state()
    
    def quit(self):
        try:
            self.process.stdin.write("QUIT\n")
            self.process.stdin.flush()
            self.process.terminate()
        except:
            pass

# 🔥 COMPILE ENGINE ON FIRST RUN
@st.cache_resource
def compile_engine():
    """Compile the C++ engine if needed"""
    engine_exe = "./chessV5_GUI"
    cpp_file = "chessV5_GUI.cpp"
    
    # Check if engine already exists and is executable
    if os.path.exists(engine_exe):
        try:
            # Test if it works
            result = subprocess.run([engine_exe], 
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   timeout=1,
                                   input="QUIT\n",
                                   text=True)
            return engine_exe, None  # Engine works!
        except:
            pass  # Need to recompile
    
    # Compile the engine
    if not os.path.exists(cpp_file):
        return None, f"❌ {cpp_file} not found in repository!"
    
    try:
        st.info("🔨 Compiling C++ engine... (this happens once)")
        
        # Compile with g++
        compile_cmd = ["g++", "-std=c++17", "-O2", cpp_file, "-o", engine_exe]
        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None, f"❌ Compilation failed:\n{result.stderr}"
        
        # Make executable (Linux/Mac)
        if platform.system() != "Windows":
            os.chmod(engine_exe, 0o755)
        
        st.success("✅ Engine compiled successfully!")
        return engine_exe, None
        
    except subprocess.TimeoutExpired:
        return None, "❌ Compilation timeout"
    except FileNotFoundError:
        return None, "❌ g++ compiler not found. Install build-essential package."
    except Exception as e:
        return None, f"❌ Compilation error: {str(e)}"

# PAGE CONFIG
st.set_page_config(
    page_title="Chess Engine GUI", 
    layout="wide", 
    page_icon="♟️"
)

st.title("♟️ Chess Engine GUI")

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'move_history' not in st.session_state:
    st.session_state.move_history = []
if 'engine_loaded' not in st.session_state:
    st.session_state.engine_loaded = False
if 'engine_path' not in st.session_state:
    st.session_state.engine_path = None

# 🔥 COMPILE ENGINE (cached, runs once)
engine_path, compile_error = compile_engine()

if compile_error:
    st.error(compile_error)
    st.info("""
    **To fix this:**
    1. Make sure `chessV5_GUI.cpp` is in your GitHub repository
    2. Add `packages.txt` with: `build-essential`
    3. The engine will auto-compile on Streamlit Cloud
    """)
    st.stop()

st.session_state.engine_path = engine_path

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Engine Settings")
    
    # Debug info
    with st.expander("🔍 Debug Info"):
        st.write(f"**OS:** {platform.system()}")
        st.write(f"**Python:** {sys.version.split()[0]}")
        st.write(f"**Working Directory:** {os.getcwd()}")
        st.write(f"**Engine Path:** {engine_path}")
        
        st.write("\n**Files in directory:**")
        try:
            files = [f for f in os.listdir('.') if not f.startswith('.')]
            for f in sorted(files)[:20]:  # Show first 20 files
                st.text(f"  📄 {f}")
        except Exception as e:
            st.error(f"Cannot list files: {e}")
        
        # Check engine
        if os.path.exists(engine_path):
            st.success(f"✅ Engine found: {engine_path}")
            st.text(f"Size: {os.path.getsize(engine_path)} bytes")
        else:
            st.error(f"❌ Engine not found: {engine_path}")
    
    # Engine controls
    st.subheader("🎮 Engine Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Load Engine", use_container_width=True):
            try:
                # Close existing engine
                if st.session_state.engine:
                    st.session_state.engine.quit()
                
                # Load engine
                st.session_state.engine = CustomChessEngine(engine_path)
                st.session_state.engine_loaded = True
                st.success("✅ Engine loaded!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to load engine: {str(e)}")
                st.session_state.engine_loaded = False
    
    with col2:
        if st.button("❌ Stop Engine", use_container_width=True):
            if st.session_state.engine:
                st.session_state.engine.quit()
            st.session_state.engine = None
            st.session_state.engine_loaded = False
            st.info("Engine stopped")
            st.rerun()
    
    # Status indicator
    if st.session_state.engine_loaded:
        st.success("🟢 Engine Running")
    else:
        st.error("🔴 Engine Stopped")
    
    st.divider()
    
    # Game controls
    st.header("🎮 Game Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("↩️ Undo", use_container_width=True, 
                    disabled=not st.session_state.engine_loaded):
            if st.session_state.engine and st.session_state.board.move_stack:
                st.session_state.engine.undo()
                st.session_state.board.pop()
                if st.session_state.move_history:
                    st.session_state.move_history.pop()
                st.rerun()
    
    with col2:
        if st.button("↪️ Redo", use_container_width=True, 
                    disabled=not st.session_state.engine_loaded):
            if st.session_state.engine:
                st.session_state.engine.redo()
                st.rerun()
    
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.move_history = []
        
        if st.session_state.engine:
            st.session_state.engine.quit()
            st.session_state.engine = CustomChessEngine(engine_path)
        
        st.rerun()
    
    st.divider()
    
    # Move history
    st.header("📜 Move History")
    
    if st.session_state.move_history:
        history_text = ""
        for i in range(0, len(st.session_state.move_history), 2):
            move_num = i // 2 + 1
            white_move = st.session_state.move_history[i]
            black_move = st.session_state.move_history[i+1] if i+1 < len(st.session_state.move_history) else "..."
            history_text += f"{move_num}. {white_move} {black_move}\n"
        
        st.text_area("Moves", history_text, height=200, disabled=True, label_visibility="collapsed")
    else:
        st.info("No moves yet")

# MAIN CONTENT
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("♟️ Chess Board")
    
    # Render board
    board_svg = chess.svg.board(st.session_state.board, size=500)
    st.image(board_svg)
    
    # Game status
    if st.session_state.board.is_checkmate():
        winner = "Black" if st.session_state.board.turn else "White"
        st.error(f"🏆 CHECKMATE! {winner} wins!")
    elif st.session_state.board.is_stalemate():
        st.warning("🤝 STALEMATE - Draw!")
    elif st.session_state.board.is_insufficient_material():
        st.warning("🤝 DRAW - Insufficient material!")
    elif st.session_state.board.is_check():
        st.warning("⚠️ CHECK!")
    else:
        st.success("✅ Game Active")

with col2:
    st.subheader("🎯 Make a Move")
    
    # Turn indicator
    turn_color = "White ⚪" if st.session_state.board.turn else "Black ⚫"
    st.info(f"**Turn:** {turn_color}")
    
    # Move input
    move_input = st.text_input(
        "Move", 
        placeholder="e2e4 or e7e8q (promotion)", 
        key="move_input",
        help="Use UCI format: from_square + to_square (e.g., e2e4, e7e8q for promotion)",
        label_visibility="collapsed"
    )
    
    # Play button
    if st.button("▶️ Play Move", use_container_width=True, type="primary"):
        if not st.session_state.engine_loaded:
            st.error("⚠️ Please load the engine first!")
        elif not move_input:
            st.warning("⚠️ Enter a move!")
        else:
            try:
                # Parse move
                move = chess.Move.from_uci(move_input.lower())
                
                # Check if legal
                if move in st.session_state.board.legal_moves:
                    # Send to engine
                    response = st.session_state.engine.send_move(move_input)
                    
                    # Check for errors
                    if any("ERROR" in line for line in response):
                        st.error("❌ Engine rejected the move!")
                    else:
                        # Update board
                        st.session_state.board.push(move)
                        st.session_state.move_history.append(move_input)
                        st.success(f"✅ Moved: {move_input}")
                        st.rerun()
                else:
                    st.error("❌ Illegal move!")
                    
            except ValueError:
                st.error("❌ Invalid move format! Use UCI notation (e.g., e2e4)")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Game info
    st.subheader("ℹ️ Game Info")
    
    col_a, col_b = st.columns(2)
    col_a.metric("Move #", st.session_state.board.fullmove_number)
    col_b.metric("Moves Made", len(st.session_state.move_history))
    
    # Legal moves count
    legal_moves_count = len(list(st.session_state.board.legal_moves))
    st.metric("Legal Moves", legal_moves_count)
    
    # Show some legal moves
    with st.expander("📋 Legal Moves"):
        legal_moves = list(st.session_state.board.legal_moves)[:20]
        moves_str = ", ".join([m.uci() for m in legal_moves])
        if len(list(st.session_state.board.legal_moves)) > 20:
            moves_str += "..."
        st.text(moves_str)

# Footer
st.divider()
st.caption("🎮 Chess Engine GUI | Powered by C++ & Streamlit")
st.caption("💡 Tip: Use UCI notation for moves (e.g., e2e4, e7e8q for pawn promotion)")
