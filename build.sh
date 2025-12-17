#!/bin/bash

echo "Compiling chess engine..."
g++ -o chessV5_GUI chessV5_GUI.cpp -std=c++11

if [ -f chessV5_GUI ]; then
    chmod +x chessV5_GUI
    echo "✅ Compilation successful!"
else
    echo "❌ Compilation failed!"
    exit 1
fi
