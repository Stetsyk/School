#!/usr/bin/env bash
# Run as the student user: bash optimize-school-linux.sh

# 1. VS Code settings (old settings saved as settings.json.bak)
mkdir -p ~/.config/Code/User
cp ~/.config/Code/User/settings.json ~/.config/Code/User/settings.json.bak 2>/dev/null
cat > ~/.config/Code/User/settings.json <<'JSON'
{
  "chat.disableAIFeatures": true,
  "telemetry.telemetryLevel": "off",
  "update.mode": "none",
  "extensions.autoUpdate": false,
  "editor.minimap.enabled": false,
  "git.enabled": false,
  "workbench.startupEditor": "none"
}
JSON

# 2. Remove heavy extensions (Python is in Thonny now)
for EXT in ms-python.python ms-python.vscode-pylance GitHub.copilot GitHub.copilot-chat; do
  code --uninstall-extension $EXT 2>/dev/null
done

# 3. Chrome: Memory Saver on, no running in background after closing
sudo mkdir -p /etc/opt/chrome/policies/managed
echo '{"HighEfficiencyModeEnabled": true, "BackgroundModeEnabled": false}' \
  | sudo tee /etc/opt/chrome/policies/managed/school.json >/dev/null

echo "Done. Restart VS Code and Chrome."
