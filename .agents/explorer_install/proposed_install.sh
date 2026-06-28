#!/usr/bin/env bash
# install.sh - Installer for gnuin-cockpit
# Designed to build a local virtual environment, deploy wrapper executable,
# and setup desktop integrations following Qt6-native guidelines.

set -euo pipefail

# Determine script directory
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# 1. Parse Arguments
PREFIX="$HOME/.local"
while [[ $# -gt 0 ]]; do
  case $1 in
    --prefix)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --prefix requires a value." >&2
        exit 1
      fi
      PREFIX="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Convert PREFIX to absolute path
PREFIX="$(mkdir -p "$PREFIX" && cd -- "$PREFIX" && pwd)"

# 2. Python Environment Checks
python_cmd=""
for cmd in python3 python; do
  if command -v "$cmd" >/dev/null 2>&1; then
    python_cmd="$cmd"
    break
  fi
done

if [[ -z "$python_cmd" ]]; then
  echo "Error: python3 not found on host. Python >= 3.10 is required." >&2
  exit 1
fi

# Verify Python Version >= 3.10
py_out=$("$python_cmd" --version 2>&1 || "$python_cmd" -V 2>&1 || "$python_cmd" 2>&1)
if [[ "$py_out" =~ Python[[:space:]]+([0-9]+)\.([0-9]+) ]]; then
  major="${BASH_REMATCH[1]}"
  minor="${BASH_REMATCH[2]}"
  if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 10 ]]; }; then
    echo "Error: Python version $major.$minor is unsupported. Python >= 3.10 is required." >&2
    exit 1
  fi
else
  echo "Error: Could not determine Python version from: $py_out" >&2
  exit 1
fi

# 3. Permissions Check
# Ensure prefix target directories are writable
BIN_DIR="$PREFIX/bin"
SHARE_DIR="$PREFIX/share/gnuin-cockpit"
VENV_DIR="$SHARE_DIR/venv"
APPS_DIR="$PREFIX/share/applications"
ICON_DIR="$PREFIX/share/icons/hicolor/scalable/apps"

mkdir -p "$BIN_DIR" "$SHARE_DIR" "$APPS_DIR" "$ICON_DIR" 2>/dev/null || {
  echo "Error: Permission denied. Prefix path '$PREFIX' is not writable." >&2
  exit 1
}

# Test touch verification
if ! touch "$PREFIX/.install_write_test" 2>/dev/null; then
  echo "Error: Permission denied. Prefix path '$PREFIX' is not writable." >&2
  exit 1
fi
rm -f "$PREFIX/.install_write_test"

# 4. Clean Pre-existing Files (handles interrupts, read-only files, and locked states)
rm -f "$BIN_DIR/gnuin-cockpit"
rm -f "$APPS_DIR/gnuin-cockpit.desktop"
rm -f "$ICON_DIR/gnuin-cockpit.svg"
rm -rf "$VENV_DIR"

# 5. Virtual Environment Creation
"$python_cmd" -m venv "$VENV_DIR"

# 6. Dependency Installation
# Install the gnuin-cockpit package itself (including PySide6 & requests dependencies)
# We execute pip inside the virtual environment
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install "$SCRIPT_DIR"

# 7. Wrapper Script Deployment
cat > "$BIN_DIR/gnuin-cockpit" <<EOF
#!/usr/bin/env bash
# Enforce native Qt styling via Wayland where applicable
export QT_QPA_PLATFORM="\${QT_QPA_PLATFORM:-wayland}"
export QT_STYLE_OVERRIDE="\${QT_STYLE_OVERRIDE:-kvantum}"
exec "$VENV_DIR/bin/gnuin-cockpit" "\$@"
EOF
chmod 0755 "$BIN_DIR/gnuin-cockpit"

# 8. Desktop File Deployment
desktop_template="$SCRIPT_DIR/data/gnuin-cockpit.desktop"
desktop_dest="$APPS_DIR/gnuin-cockpit.desktop"

if [[ -f "$desktop_template" ]]; then
  sed \
    -e "s|^Exec=.*|Exec=$BIN_DIR/gnuin-cockpit|g" \
    -e "s|^Icon=.*|Icon=gnuin-cockpit|g" \
    "$desktop_template" > "$desktop_dest"
else
  # Fallback desktop generation if template is missing
  cat > "$desktop_dest" <<EOF
[Desktop Entry]
Name=GNU.IN Pipeline Cockpit
Comment=A fast local Qt6 control panel for GNU.IN multi-repo pipeline
Exec=$BIN_DIR/gnuin-cockpit
Icon=gnuin-cockpit
Terminal=false
Type=Application
Categories=Development;Utility;
Keywords=Git;Pipeline;Status;
StartupNotify=true
# Enforce native Qt styling via Wayland where applicable
Environment=QT_QPA_PLATFORM=wayland;QT_STYLE_OVERRIDE=kvantum
EOF
fi
chmod 0644 "$desktop_dest"

# 9. Desktop Icon Deployment
# Locate the source app icon from design reference (either sibling or nested directory)
source_icon=""
for path in \
  "$SCRIPT_DIR/../gnu.in-design-reference/assets/symbols/app-icon.svg" \
  "$SCRIPT_DIR/gnu.in-design-reference/assets/symbols/app-icon.svg" \
  "$(dirname "$SCRIPT_DIR")/gnu.in-design-reference/assets/symbols/app-icon.svg"; do
  if [[ -f "$path" ]]; then
    source_icon="$path"
    break
  fi
done

if [[ -n "$source_icon" ]]; then
  cp "$source_icon" "$ICON_DIR/gnuin-cockpit.svg"
else
  # Embedded SVG fallback if no design asset found
  cat > "$ICON_DIR/gnuin-cockpit.svg" <<EOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <rect width="100" height="100" rx="20" fill="#1e1e2e"/>
  <path d="M30,70 L50,30 L70,70 Z" fill="none" stroke="#89b4fa" stroke-width="8" stroke-linejoin="round"/>
  <circle cx="50" cy="50" r="10" fill="#f38ba8"/>
</svg>
EOF
fi
chmod 0644 "$ICON_DIR/gnuin-cockpit.svg"

echo "Installation complete!"
echo "  Executable: $BIN_DIR/gnuin-cockpit"
echo "  Desktop entry: $desktop_dest"
echo "  Icon: $ICON_DIR/gnuin-cockpit.svg"
