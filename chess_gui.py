import streamlit as st
import subprocess
import chess
import chess.svg
import re
import platform

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
        # Read initial board state
        self.read_state()
    
    def read_state(self):
        """Read the engine's output until we get the full state"""
        lines = []
        while True:
            line = self.process.stdout.readline().strip()
            if not line:
                break
            lines.append(line)
            if line.startswith("STATUS"):
                break
        return lines
    
    def send_move(self, move_str):
        """Send a move like 'e2e4' to the engine"""
        command = f"MOVE {move_str}\n"
        self.process.stdin.write(command)
        self.process.stdin.flush()
        return self.read_state()
    
    def undo(self):
        """Send UNDO command"""
        self.process.stdin.write("UNDO\n")
        self.process.stdin.flush()
        return self.read_state()
    
    def redo(self):
        """Send REDO command"""
        self.process.stdin.write("REDO\n")
        self.process.stdin.flush()
        return self.read_state()
    
    def quit(self):
        """Close the engine"""
        self.process.stdin.write("QUIT\n")
        self.process.stdin.flush()
        self.process.terminate()

# Streamlit App
st.set_page_config(page_title="Chess Engine GUI", layout="wide")
st.title("♟️ Chess Engine GUI")

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'engine' not in st.session_state:
    st.session_state.engine = None
if 'move_history' not in st.session_state:
    st.session_state.move_history = []

# Engine setup section
with st.sidebar:
    st.header("⚙️ Engine Settings")
    
    # Default path
    if platform.system() == "Windows":
        default_path = r"D:\VS Code\cpp\chess\chessV5_GUI.exe"
    else:
        default_path = "./chessV5_GUI"
    
    engine_path = st.text_input("Engine Path", default_path)
    
    col1, col2 = st.columns(2)
    
    if st.button("🚀 Load Engine", use_container_width=True):
        try:
            st.session_state.engine = CustomChessEngine(engine_path)
            st.success("✅ Engine loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading engine: {e}")
    
    st.divider()
    
    # Game controls
    st.header("🎮 Game Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Undo", use_container_width=True):
            if st.session_state.engine:
                st.session_state.engine.undo()
                if len(st.session_state.board.move_stack) > 0:
                    st.session_state.board.pop()
                st.rerun()
    
    with col2:
        if st.button("↪️ Redo", use_container_width=True):
            if st.session_state.engine:
                st.session_state.engine.redo()
                st.rerun()
    
    if st.button("🔄 Reset Game", use_container_width=True):
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
        for i, move in enumerate(st.session_state.move_history, 1):
            st.text(f"{i}. {move}")
    else:
        st.text("No moves yet")

# Main board area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("♟️ Chess Board")
    
    # Display the board
    board_svg = chess.svg.board(
        st.session_state.board,
        size=450
    )
    st.image(board_svg)
    
    # Game status
    if st.session_state.board.is_checkmate():
        st.error("🏆 CHECKMATE!")
    elif st.session_state.board.is_stalemate():
        st.warning("🤝 STALEMATE!")
    elif st.session_state.board.is_check():
        st.warning("⚠️ CHECK!")

with col2:
    st.subheader("🎯 Make a Move")
    
    # Move input
    st.info("Enter moves in format: **e2e4** (from-square to-square)")
    
    move_input = st.text_input(
        "Your move",
        placeholder="e.g., e2e4, e7e8q (for promotion)",
        key="move_input"
    )
    
    if st.button("▶️ Play Move", use_container_width=True):
        if not st.session_state.engine:
            st.error("⚠️ Please load the engine first!")
        elif move_input:
            try:
                # Try to make the move on python-chess board first
                move = chess.Move.from_uci(move_input)
                
                if move in st.session_state.board.legal_moves:
                    # Valid move - send to engine
                    response = st.session_state.engine.send_move(move_input)
                    
                    # Check if engine accepted the move
                    if any("ERROR" in line for line in response):
                        st.error("❌ Engine rejected the move!")
                    else:
                        # Update python-chess board
                        st.session_state.board.push(move)
                        st.session_state.move_history.append(move_input)
                        st.success(f"✅ Move played: {move_input}")
                        st.rerun()
                else:
                    st.error("❌ Illegal move!")
                    
            except Exception as e:
                st.error(f"❌ Invalid move format: {e}")
    
    st.divider()
    
    # Quick move buttons for common pieces
    st.subheader("🎲 Quick Moves")
    st.caption("Click a square on the board above, then enter your move manually")
    
    # Game info
    st.divider()
    st.subheader("ℹ️ Game Info")
    st.text(f"Turn: {'White' if st.session_state.board.turn else 'Black'}")
    st.text(f"Move #: {st.session_state.board.fullmove_number}")
    st.text(f"Total moves: {len(st.session_state.move_history)}")

# Footer
st.divider()

st.caption("🎮 Chess Engine GUI | Made with Streamlit & C++")
