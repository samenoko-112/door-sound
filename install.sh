#! /bin/bash
set -e

PROJECT_NAME="door-sound"
PROJECT_BASE_DIR="$HOME/$PROJECT_NAME"


echo "=== System Update & Upgrade ==="
sudo apt-get update
sudo apt-get upgrade -y

echo "=== Install python3-dev ==="
sudo apt-get install python3-dev -y

if [ "$EUID" -eq 0 ]; then
  echo "Error: This script should not be run as root. Run it as the user who will own the service."
  exit 1
fi

echo "=== Create Project Directory: $PROJECT_BASE_DIR ==="
mkdir -p "$PROJECT_BASE_DIR"
cd "$PROJECT_BASE_DIR"

echo "=== Create venv in $PROJECT_BASE_DIR/venv ==="
python3 -m venv venv

echo "=== Activate venv and install dependencies ==="
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "=== Create systemd user service directory ==="
mkdir -p ~/.config/systemd/user

echo "=== Copy service file ==="
if [ ! -f "doorsound.service" ]; then
    echo "Error: doorsound.service not found in $PROJECT_BASE_DIR. Please place it there."
    exit 1
fi
cp doorsound.service ~/.config/systemd/user/

echo "=== Reload systemd, enable and start service ==="
systemctl --user daemon-reload
systemctl --user enable doorsound
systemctl --user start doorsound

echo "=== Setup Finished ==="
echo "Important: If this service needs to run when you are not logged in,"
echo "you MUST enable lingering for user $(whoami) by running:"
echo "sudo loginctl enable-linger $(whoami)"
echo "Then reboot or restart the user's systemd instance."