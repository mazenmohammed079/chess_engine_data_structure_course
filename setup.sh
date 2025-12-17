#!/bin/bash

echo "Setting up chess engine..."
g++ -o chessV5_GUI chess_engine.cpp -std=c++11
chmod +x chessV5_GUI
echo "Setup complete!"