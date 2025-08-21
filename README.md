# Terminal Music Player

[
[
[

A lightweight, terminal-based media player with a curses interface inspired by nmtui design. Browse and play your music collection directly from the command line with an intuitive, keyboard-driven interface.



## ✨ Features

- 🔀 **Shuffle Mode**: Automatic random playback
- ⌨️ **Keyboard Controls**: Full keyboard navigation
- 🎨 **Clean Interface**: nmtui-inspired terminal UI
- 🚀 **Lightweight**: No heavy dependencies, pure Python

## 📋 Requirements

- **Python**: 3.6 or higher
- **Media Player** (one of the following):
  - `mpv` (recommended)
  - `mplayer`
  - `vlc`

## 🚀 Installation

### 1. Install Media Player

**Ubuntu/Debian:**
```bash
sudo apt install mpv
```

**macOS:**
```bash
brew install mpv
```

**Fedora:**
```bash
sudo dnf install mpv
```

**Arch Linux:**
```bash
sudo pacman -S mpv
```

### 2. Download the Script

```bash
# Clone or download the script
wget https://raw.githubusercontent.com/username/terminal-music-player/main/mpv_tui.py
chmod +x mpv_tui.py
```

## 📖 Usage

### Basic Usage

```bash
# Play files from current directory
python3 mpv_tui.py

# Play files from specific directory
python3 mpv_tui.py /path/to/music

# Play files from home music directory
python3 mpv_tui.py ~/Music

# Play files from directory with spaces
python3 mpv_tui.py "My Music Folder"
```

### Command Line Options

```bash
# Show help
python3 mpv_tui.py --help

# Show version
python3 mpv_tui.py --version
```

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate up/down through files |
| `PgUp` `PgDn` | Page up/down |
| `Home` `End` | Jump to first/last file |
| `Enter` | Play selected file |
| `Space` | Stop current playback |
| `s` | Toggle shuffle mode |
| `r` | Play random file |
| `q` `Esc` | Quit application |

## 🎨 Interface Preview


### Integration with Shell

```bash
# Create an alias for convenience
echo 'alias music="python3 /path/to/mpv_tui.py"' >> ~/.bashrc
source ~/.bashrc

# Now use it simply
music ~/Music
```

### Performance Tips

- For large directories (1000+ files), consider organizing into subdirectories
- Use SSD storage for better file listing performance
- Ensure sufficient terminal size (minimum 80x24)
