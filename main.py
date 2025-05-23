#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ドアの開閉を検知して音声を再生するプログラム
- GPIOピンでドアセンサーの状態を監視
- ドアが開いたときにランダムな音声を再生
- テストモード時はログを記録
"""

import RPi.GPIO as GPIO
import pygame
import os
import random
import time
import signal
import sys
import logging
from datetime import datetime

# ===== 基本設定 =====
# スクリプトの絶対パスを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== テストモード設定 =====
TEST_MODE = True  # テストモードのフラグ

# ===== ログ設定 =====
if TEST_MODE:
    # ログディレクトリの作成と設定
    log_dir = os.path.join(SCRIPT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"door_sound_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # ログの基本設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# ===== サウンド設定 =====
SOUNDS_DIR = os.path.join(SCRIPT_DIR, "sounds")  # サウンドファイルのディレクトリ
ALLOWED_EXTENSIONS = [".wav", ".mp3"]  # 再生可能な音声ファイルの拡張子

# ===== GPIO設定 =====
# GPIOピンの番号付け方式をBCM (Broadcom SOC channel) に設定
GPIO.setmode(GPIO.BCM)

# ドアセンサーを接続するGPIOピン番号
# BCMモードのGPIO 11番ピンを使用
DOOR_SENSOR_PIN = 11

# GPIOピンを入力モードに設定し、内部プルアップ抵抗を有効化
# スイッチOFF(ドア開)でHIGH、ON(ドア閉)でLOWになる想定
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ===== デバウンス設定 =====
# チャタリング（短時間のON/OFFの繰り返し）を無視する時間（秒）
# この時間内の状態変化は無視され、安定するまで待機
DEBOUNCE_TIME_S = 0.2

# ===== サウンド再生関数 =====
def get_random_sound_file():
    """
    指定されたディレクトリからランダムなサウンドファイルパスを取得する
    
    Returns:
        str or None: サウンドファイルのパス。ファイルが見つからない場合はNone
    """
    sound_files = []
    try:
        for filename in os.listdir(SOUNDS_DIR):
            if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                sound_files.append(os.path.join(SOUNDS_DIR, filename))
    except FileNotFoundError:
        error_msg = f"エラー: ディレクトリ '{SOUNDS_DIR}' が見つかりません。"
        if TEST_MODE:
            logging.error(error_msg)
        print(error_msg)
        return None
    except Exception as e:
        error_msg = f"サウンドファイルの検索中にエラーが発生しました: {e}"
        if TEST_MODE:
            logging.error(error_msg)
        print(error_msg)
        return None

    if not sound_files:
        error_msg = f"エラー: ディレクトリ '{SOUNDS_DIR}' にサウンドファイルが見つかりません。"
        if TEST_MODE:
            logging.error(error_msg)
        print(error_msg)
        return None

    selected_file = random.choice(sound_files)
    if TEST_MODE:
        logging.info(f"選択されたサウンドファイル: {selected_file}")
    return selected_file

def play_sound(file_path):
    """
    指定されたファイルパスのサウンドを再生する
    
    Args:
        file_path (str): 再生するサウンドファイルのパス
    """
    if file_path:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            log_msg = f"再生中: {file_path}"
            if TEST_MODE:
                logging.info(log_msg)
            print(log_msg)
        except pygame.error as e:
            error_msg = f"サウンド再生エラー '{file_path}': {e}"
            if TEST_MODE:
                logging.error(error_msg)
            print(error_msg)

# ===== シグナルハンドラ =====
def signal_handler(signum, frame):
    """
    シグナルを受け取ったときの処理
    
    Args:
        signum: 受信したシグナル番号
        frame: 現在のスタックフレーム
    """
    log_msg = f"\nシグナル {signum} を受信しました。終了処理を開始します..."
    if TEST_MODE:
        logging.info(log_msg)
    print(log_msg)
    # GPIO設定をクリーンアップ
    GPIO.cleanup()
    # Pygame Mixerを終了
    pygame.mixer.quit()
    log_msg = "リソースを解放しました。"
    if TEST_MODE:
        logging.info(log_msg)
    print(log_msg)
    sys.exit(0)

# SIGTERMとSIGINTのハンドラを設定
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# ===== メイン処理 =====
if __name__ == "__main__":
    if TEST_MODE:
        logging.info("=== ドアサウンドプログラム開始 ===")
        logging.info(f"テストモード: 有効")
        logging.info(f"ログファイル: {log_file}")

    # Pygame Mixerの初期化
    try:
        pygame.mixer.init()
    except pygame.error as e:
        error_msg = f"Pygameミキサーの初期化に失敗しました: {e}"
        if TEST_MODE:
            logging.error(error_msg)
        print(error_msg)
        print("オーディオデバイスが利用可能か、またはライブラリが正しくインストールされているか確認してください。")
        exit()

    log_msg = "ドアセンサー監視中... (Ctrl+Cで終了)"
    if TEST_MODE:
        logging.info(log_msg)
    print(log_msg)

    # 状態を管理するための変数 (デバウンス用)
    previous_raw_reading = GPIO.input(DOOR_SENSOR_PIN)
    last_stable_state = previous_raw_reading
    time_of_last_raw_change = time.time()

    # プログラム開始時のセンサー状態を表示
    current_time_str = time.strftime('%H:%M:%S')
    if last_stable_state == GPIO.LOW:  # ドアが閉じている
        log_msg = f"[{current_time_str}] ドアが閉まりました (初期状態)"
    else:  # ドアが開いている
        log_msg = f"[{current_time_str}] ドアが開きました (初期状態)"
    
    if TEST_MODE:
        logging.info(log_msg)
    print(log_msg)

    try:
        # メインループ：センサーの状態を定期的にチェック
        while True:
            current_raw_reading = GPIO.input(DOOR_SENSOR_PIN)

            if current_raw_reading != previous_raw_reading:
                time_of_last_raw_change = time.time()

            if (time.time() - time_of_last_raw_change) >= DEBOUNCE_TIME_S:
                if current_raw_reading != last_stable_state:
                    last_stable_state = current_raw_reading
                    current_time_str = time.strftime('%H:%M:%S')

                    if last_stable_state == GPIO.HIGH:  # ドアが開いたと判定
                        log_msg = f"[{current_time_str}] ドアが開きました"
                        if TEST_MODE:
                            logging.info(log_msg)
                        print(log_msg)
                        # サウンド再生処理
                        sound_file_to_play = get_random_sound_file()
                        play_sound(sound_file_to_play)
                    else:  # ドアが閉じたと判定
                        log_msg = f"[{current_time_str}] ドアが閉まりました"
                        if TEST_MODE:
                            logging.info(log_msg)
                        print(log_msg)
            
            previous_raw_reading = current_raw_reading
            time.sleep(0.02)  # ポーリング間隔 (20ミリ秒)

    except Exception as e:
        error_msg = f"\n予期せぬエラーが発生しました: {e}"
        if TEST_MODE:
            logging.error(error_msg)
        print(error_msg)
        # エラー発生時もクリーンアップを実行
        GPIO.cleanup()
        pygame.mixer.quit()
        sys.exit(1)

    finally:
        # プログラム終了時のクリーンアップ
        GPIO.cleanup()
        pygame.mixer.quit()
        log_msg = "リソースを解放しました。"
        if TEST_MODE:
            logging.info(log_msg)
        print(log_msg)
