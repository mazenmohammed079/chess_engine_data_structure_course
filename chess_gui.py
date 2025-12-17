import streamlit as st
import subprocess
import chess
import chess.svg
import time
import platform
import os

class CustomChessEngine:
    def __init__(self, engine_path):
        self.process = subprocess.Popen(engine_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
        self.read_state()
    
    def read_state(self):
        lines = []
        for _ in range(20):
            line = self.process.stdout.readline().strip()
            if line: lines.append(line)
            if "STATUS" in line: break
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
        self.process.stdin.write("QUIT\n")
        self.process.stdin.flush()
        self.process.terminate()

st.set_page_config(page_title="Chess Engine GUI", layout="wide", page_icon="♟️")
st.title("♟️ Chess Engine GUI")

if 'board' not in st.session_state: st.session_state.board = chess.Board()
if 'engine' not in st.session_state: st.session_state.engine = None
if 'move_history' not in st.session_state: st.session_state.move_history = []
if 'engine_loaded' not in st.session_state: st.session_state.engine_loaded = False

with st.sidebar:
    st.header("⚙️ Engine Settings")
    
    # 🔥 DEBUG SECTION - Shows what's happening
    with st.expander("🔍 Debug Info (Click to expand)"):
        st.write(f"**OS:** {platform.system()}")
        st.write(f"**Working Directory:** {os.getcwd()}")
        st.write(f"**Files in folder:**")
        try:
            files = os.listdir('.')
            for f in files:
                st.text(f"  - {f}")
        except:
            st.error("Cannot list files")
        
        st.write("**Engine Check:**")
        if os.path.exists("./chessV5_GUI"):
            st.success("✅ chessV5_GUI found!")
        else:
            st.error("❌ chessV5_GUI NOT found!")
        
        if os.path.exists("chess_engine.cpp"):
            st.success("✅ chess_engine.cpp found!")
        else:
            st.error("❌ chess_engine.cpp NOT found!")
    
    # Auto-detect engine path
    if platform.system() == "Windows":
        default_path = r"D:\VS Code\cpp\chess\chessV5_GUI.exe"
    else:
        default_path = "./chessV5_GUI"
    
    engine_path = st.text_input("Engine Path", default_path)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Load", use_container_width=True):
            try:
                if st.session_state.engine: st.session_state.engine.quit()
                st.session_state.engine = CustomChessEngine(engine_path)
                st.session_state.engine_loaded = True
                st.success("✅ Loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
    with col2:
        if st.button("❌ Stop", use_container_width=True):
            if st.session_state.engine: st.session_state.engine.quit()
            st.session_state.engine = None
            st.session_state.engine_loaded = False
    
    st.success("🟢 Running") if st.session_state.engine_loaded else st.error("🔴 Stopped")
    st.divider()
    
    st.header("🎮 Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Undo", use_container_width=True, disabled=not st.session_state.engine_loaded):
            st.session_state.engine.undo()
            if st.session_state.board.move_stack:
                st.session_state.board.pop()
                if st.session_state.move_history: st.session_state.move_history.pop()
            st.rerun()
    with col2:
        if st.button("↪️ Redo", use_container_width=True, disabled=not st.session_state.engine_loaded):
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
    st.header("📜 Move History")
    if st.session_state.move_history:
        for i in range(0, len(st.session_state.move_history), 2):
            w = st.session_state.move_history[i]
            b = st.session_state.move_history[i+1] if i+1 < len(st.session_state.move_history) else "..."
            st.text(f"{i//2 + 1}. {w} {b}")
    else:
        st.text("No moves yet")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("♟️ Chess Board")
    st.image(chess.svg.board(st.session_state.board, size=500))
    
    if st.session_state.board.is_checkmate():
        winner = "Black" if st.session_state.board.turn else "White"
        st.error(f"🏆 CHECKMATE! {winner} wins!")
    elif st.session_state.board.is_stalemate():
        st.warning("🤝 STALEMATE!")
    elif st.session_state.board.is_check():
        st.warning("⚠️ CHECK!")
    else:
        st.success("✅ Active")

with col2:
    st.subheader("🎯 Make a Move")
    turn = "White ⚪" if st.session_state.board.turn else "Black ⚫"
    st.info(f"**Turn:** {turn}")
    
    move_input = st.text_input("Move", placeholder="e2e4", key="move_input", label_visibility="collapsed")
    
    if st.button("▶️ Play", use_container_width=True, type="primary"):
        if not st.session_state.engine_loaded:
            st.error("⚠️ Load engine first!")
        elif move_input:
            try:
                move = chess.Move.from_uci(move_input.lower())
                if move in st.session_state.board.legal_moves:
                    response = st.session_state.engine.send_move(move_input)
                    if not any("ERROR" in line for line in response):
                        st.session_state.board.push(move)
                        st.session_state.move_history.append(move_input)
                        st.rerun()
                    else:
                        st.error("❌ Engine rejected!")
                else:
                    st.error("❌ Illegal!")
            except:
                st.error("❌ Invalid format!")
    
    st.divider()
    st.subheader("ℹ️ Info")
    c1, c2 = st.columns(2)
    c1.metric("Move #", st.session_state.board.fullmove_number)
    c2.metric("Total", len(st.session_state.move_history))

st.divider()
st.caption("🎮 Chess Engine GUI | Streamlit & C++")
