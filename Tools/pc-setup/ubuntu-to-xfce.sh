#!/usr/bin/env bash
# Make an existing Ubuntu machine look and run like a light XFCE desktop
# (same layout as Linux Mint XFCE / Xubuntu) without reinstalling.
# Usage: sudo bash ubuntu-to-xfce.sh   then reboot.
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Run with sudo: sudo bash $0"; exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> 1/6 Installing light XFCE desktop (xubuntu-core) + LightDM login screen"
echo "lightdm shared/default-x-display-manager select lightdm" | debconf-set-selections
echo "gdm3 shared/default-x-display-manager select lightdm" | debconf-set-selections
apt-get update
apt-get install -y xubuntu-core lightdm lightdm-gtk-greeter zram-tools

echo "==> 2/6 Making LightDM the login screen"
echo /usr/sbin/lightdm > /etc/X11/default-display-manager
ln -sf /lib/systemd/system/lightdm.service /etc/systemd/system/display-manager.service

echo "==> 3/6 Making XFCE the default session for everyone"
SESSION=xfce
[ -f /usr/share/xsessions/xubuntu.desktop ] && SESSION=xubuntu
mkdir -p /etc/lightdm/lightdm.conf.d
printf "[Seat:*]\nuser-session=%s\n" "$SESSION" > /etc/lightdm/lightdm.conf.d/50-default-session.conf
# Existing users may have GNOME remembered as their last session; switch them too
for f in /var/lib/AccountsService/users/*; do
  [ -f "$f" ] || continue
  if grep -q '^XSession=' "$f"; then
    sed -i "s/^XSession=.*/XSession=$SESSION/" "$f"
  else
    echo "XSession=$SESSION" >> "$f"
  fi
done

echo "==> 4/6 Mint-like layout: taskbar at the bottom for every user"
# Runs once at each user's first XFCE login (existing and new users) and moves
# the main panel to the bottom edge, like Linux Mint XFCE.
cat > /usr/local/bin/school-panel-bottom.sh <<'EOF'
#!/usr/bin/env bash
MARK="$HOME/.config/school-panel-bottom.done"
[ -f "$MARK" ] && exit 0
sleep 5   # let the panel start first
ID=$(xfconf-query -c xfce4-panel -p /panels 2>/dev/null | grep -E '^[0-9]+$' | head -n1)
[ -n "$ID" ] || exit 0
xfconf-query -c xfce4-panel -p /panels/panel-$ID/position -s "p=8;x=0;y=0" &&
xfconf-query -c xfce4-panel -p /panels/panel-$ID/position-locked -n -t bool -s true 2>/dev/null ||
xfconf-query -c xfce4-panel -p /panels/panel-$ID/position-locked -s true
mkdir -p "$HOME/.config" && touch "$MARK"
EOF
chmod +x /usr/local/bin/school-panel-bottom.sh
cat > /etc/xdg/autostart/school-panel-bottom.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=School: panel at the bottom
Exec=/usr/local/bin/school-panel-bottom.sh
OnlyShowIn=XFCE;
NoDisplay=true
EOF

echo "==> 5/6 Optimisations: compressed RAM (zram) + swap tuning"
cat > /etc/default/zramswap <<EOF
ALGO=zstd
PERCENT=50
EOF
systemctl enable --now zramswap || true
echo "vm.swappiness=100" > /etc/sysctl.d/99-zram.conf
sysctl -p /etc/sysctl.d/99-zram.conf >/dev/null

echo "==> 6/6 Optimisations: turning off background services not needed in a classroom"
# crash reporters
systemctl disable --now apport.service whoopsie.service 2>/dev/null || true
# GNOME file indexer (eats CPU/disk on old machines); names differ by Ubuntu version
systemctl --global mask tracker-miner-fs-3.service localsearch-3.service 2>/dev/null || true

echo
echo "Done. Reboot now:  sudo reboot"
echo "Log in as usual - the desktop will be XFCE (taskbar at the bottom)."
