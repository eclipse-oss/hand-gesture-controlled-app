#!/usr/bin/env bash
set -e

echo "[1/5] Installing system dependencies via pacman..."
sudo pacman -S --needed base-devel python312

echo "[2/5] Creating Python 3.12 virtual environment..."
python3.12 -m venv venv

echo "[3/5] Activating virtual environment..."
source venv/bin/activate

echo "[4/5] Upgrading pip..."
pip install --upgrade pip

echo "[5/5] Installing Python libraries..."
pip install "mediapipe<=0.10.21" opencv-python uinput

echo "--------------------------------------------------"
echo "[SUCCESS] Environment is ready!"
echo "To activate it manually in the future, run: source venv/bin/activate"
echo "To start the application, run: python main.py"
echo "-------------------------------------------------