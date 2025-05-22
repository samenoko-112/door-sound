import RPi.GPIO as GPIO
import pygame
import os
import random
import time
import signal
import sys

# --- サウンド関連の設定 ---
SOUNDS_DIR = "./sounds"  # サウンドファイルが格納されているディレクトリ
ALLOWED_EXTENSIONS = [".wav", ".mp3"] # 再生を許可する拡張子

# --- GPIO関連の設定 ---
# GPIOピンの番号付け方式をBCM (Broadcom SOC channel) に設定
GPIO.setmode(GPIO.BCM)

# ドアセンサーを接続するGPIOピン番号
# BCMモードのGPIO 3番ピン (物理ピン番号では5番ピン) を使用
DOOR_SENSOR_PIN = 11

# GPIOピンを入力モードに設定し、内部プルアップ抵抗を有効にする
# これにより、スイッチOFF(ドア開)でHIGH、ON(ドア閉)でLOWになる想定
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- デバウンス処理のための設定 ---
# チャタリング（短時間のON/OFFの繰り返し）を無視する時間（秒単位）。
# この時間内に状態が再度変化しても、安定するまでは最終的な状態変化として認識しない。
# 0.1秒でチャタリングが収まらない場合は、0.3秒や0.5秒など、長めの値に調整してください。
DEBOUNCE_TIME_S = 0.2

# --- サウンド再生のための関数 ---
def get_random_sound_file():
    """指定されたディレクトリからランダムなサウンドファイルパスを取得する"""
    sound_files = []
    try:
        for filename in os.listdir(SOUNDS_DIR):
            if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                sound_files.append(os.path.join(SOUNDS_DIR, filename))
    except FileNotFoundError:
        print(f"エラー: ディレクトリ '{SOUNDS_DIR}' が見つかりません。")
        return None
    except Exception as e:
        print(f"サウンドファイルの検索中にエラーが発生しました: {e}")
        return None

    if not sound_files:
        print(f"エラー: ディレクトリ '{SOUNDS_DIR}' にサウンドファイルが見つかりません。")
        return None

    return random.choice(sound_files)

def play_sound(file_path):
    """指定されたファイルパスのサウンドを再生する"""
    if file_path:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"再生中: {file_path}")
        except pygame.error as e:
            print(f"サウンド再生エラー '{file_path}': {e}")

# --- シグナルハンドラの設定 ---
def signal_handler(signum, frame):
    """シグナルを受け取ったときの処理"""
    print(f"\nシグナル {signum} を受信しました。終了処理を開始します...")
    # GPIO設定をクリーンアップ
    GPIO.cleanup()
    # Pygame Mixerを終了
    pygame.mixer.quit()
    print("リソースを解放しました。")
    sys.exit(0)

# SIGTERMとSIGINTのハンドラを設定
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# --- メイン処理 ---
if __name__ == "__main__":
    # Pygame Mixerの初期化
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Pygameミキサーの初期化に失敗しました: {e}")
        print("オーディオデバイスが利用可能か、またはライブラリが正しくインストールされているか確認してください。")
        exit()

    print("ドアセンサー監視中... (Ctrl+Cで終了)")

    # --- 状態を管理するための変数 (デバウンス用) ---
    previous_raw_reading = GPIO.input(DOOR_SENSOR_PIN)
    last_stable_state = previous_raw_reading
    time_of_last_raw_change = time.time()

    # --- プログラム開始時のセンサー状態を表示 ---
    current_time_str = time.strftime('%H:%M:%S')
    if last_stable_state == GPIO.LOW: # ドアが閉じている
        print(f"[{current_time_str}] ドアが閉まりました (初期状態)")
    else: # ドアが開いている
        print(f"[{current_time_str}] ドアが開きました (初期状態)")
        # 初期状態でドアが開いていたら音を鳴らす (オプション)
        # sound_file = get_random_sound_file()
        # play_sound(sound_file)

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

                    if last_stable_state == GPIO.HIGH: # ドアが開いたと判定
                        print(f"[{current_time_str}] ドアが開きました")
                        # --- サウンド再生処理 ---
                        sound_file_to_play = get_random_sound_file()
                        play_sound(sound_file_to_play)
                        # -----------------------
                    else: # ドアが閉じたと判定 (last_stable_state == GPIO.LOW)
                        print(f"[{current_time_str}] ドアが閉まりました")
                        # ドアが閉じたときにも音を鳴らしたい場合は、ここに処理を追加
            
            previous_raw_reading = current_raw_reading
            time.sleep(0.02) # ポーリング間隔 (20ミリ秒)

    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
        # エラー発生時もクリーンアップを実行
        GPIO.cleanup()
        pygame.mixer.quit()
        sys.exit(1)

    finally:
        # プログラム終了時にGPIO設定をクリーンアップ
        GPIO.cleanup()
        # Pygame Mixerを終了
        pygame.mixer.quit()
        print("リソースを解放しました。")
