# DoorSound

## このプログラムについて
ドアセンサーでドアの開閉を検知し音を流すだけのプログラムです。  

## 開発環境
- Raspberry Pi 3 Model B+ (1GB RAM)
- SPS-320

リードスイッチのためSPS-320の片方の線はGNDに配線すること。

## セットアップ
install.shを実行すると勝手にセットアップされます。(楽ですね)

### セットアップスクリプトの内容
- **システムの更新**  
    システムの更新を行います。
- **必須パッケージのインストール**  
    依存関係がインストールされます。  
    python3-devとsambaです。
- **音源フォルダの作成**  
    ファイルをsambaで管理するためシンボリックリンクを作成します
- **sambaの設定**  
    sambaの設定ファイルにディレクティブを追加・パスワードの設定を行います。
- **実行準備**  
    venvの作成・pipパッケージのインストール・サービスファイルの配置を行います。
- **ポストプロセッシング**  
    ユーザー設定の変更やサービスの有効化を行います。

スクリプトを実行した後、再起動を行うと使えるようになります。

## 音源ファイルの配置
特別なソフトウェアやコマンドを必要とせず配置できるようにしました。(嬉しいね)

エクスプローラーを開きアドレスバーに`\\doorsound.local\door-sound`と入力しEnter  
ユーザー名とパスワードを入れればフォルダが開きます。

その中にファイルをぶっ込んでください。mp3ファイルとwavファイルに対応しています。