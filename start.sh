#!/bin/bash

# --- 設定 ---
VENV_DIR_NAME="venv"
PYTHON_SCRIPT_NAME="main.py"

# --- スクリプト本体 ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$SCRIPT_DIR/$VENV_DIR_NAME"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"
PYTHON_SCRIPT_PATH="$SCRIPT_DIR/$PYTHON_SCRIPT_NAME"

# 仮想環境とPythonスクリプトの存在確認 (簡略化)
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "エラー: 仮想環境が見つかりません ($ACTIVATE_SCRIPT)"
    exit 1
fi
if [ ! -f "$PYTHON_SCRIPT_PATH" ]; then
    echo "エラー: Pythonスクリプトが見つかりません ($PYTHON_SCRIPT_PATH)"
    exit 1
fi

# 仮想環境をアクティベート
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Pythonスクリプトを実行
python3 "$PYTHON_SCRIPT_PATH"

exit 0
