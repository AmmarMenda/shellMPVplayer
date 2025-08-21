#!/usr/bin/env python3

import curses
import os
import subprocess
import signal
import time
import random
import threading
import argparse
from pathlib import Path
from typing import List, Optional

# Constants
MAX_FILES = 1024
REFRESH_DELAY = 0.05  # 50ms in seconds
MAX_FILENAME_LEN = 256

# Audio/video file extensions
MEDIA_EXTENSIONS = {
    '.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma', '.opus',
    '.mp4', '.avi', '.mkv', '.mov', '.webm'
}

class PlayerState:
    """Global state management"""
    def __init__(self):
        self.child_finished = False
        self.mpv_process: Optional[subprocess.Popen] = None
        self.needs_redraw = True
        self.lock = threading.Lock()

    def set_process(self, process: Optional[subprocess.Popen]):
        with self.lock:
            self.mpv_process = process

    def get_process(self) -> Optional[subprocess.Popen]:
        with self.lock:
            return self.mpv_process

class MediaPlayer:
    def __init__(self, directory: str = "."):
        self.state = PlayerState()
        self.directory = Path(directory).resolve()
        self.files: List[str] = []
        self.highlight = 0
        self.start_index = 0
        self.shuffle_mode = False
        self.stdscr = None

        # Start background thread to monitor child processes
        self.monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self.monitor_thread.start()

    def _monitor_processes(self):
        """Background thread to monitor child processes"""
        while True:
            process = self.state.get_process()
            if process and process.poll() is not None:
                self.state.set_process(None)
                self.state.child_finished = True
                self.state.needs_redraw = True
            time.sleep(0.1)

    def is_media_file(self, filename: str) -> bool:
        """Check if file has media extension"""
        return Path(filename).suffix.lower() in MEDIA_EXTENSIONS

    def load_media_files(self) -> int:
        """Load media files from specified directory"""
        try:
            if not self.directory.exists():
                raise OSError(f"Directory does not exist: {self.directory}")

            if not self.directory.is_dir():
                raise OSError(f"Path is not a directory: {self.directory}")

            # Change to the target directory for playback
            original_cwd = Path.cwd()
            os.chdir(self.directory)

            entries = os.listdir('.')
            self.files = []

            for entry in entries:
                if (os.path.isfile(entry) and
                    not entry.startswith('.') and
                    self.is_media_file(entry)):
                    self.files.append(entry)

            self.files.sort()  # Sort alphabetically
            return len(self.files)

        except (OSError, PermissionError) as e:
            # Restore original directory if there was an error
            try:
                os.chdir(original_cwd)
            except:
                pass
            raise e

    def play_file(self, filename: str) -> bool:
        """Play media file using available player"""
        self.stop_playback()

        # Use absolute path to ensure correct file is played
        filepath = self.directory / filename

        # Try different media players in order of preference
        players = [
            ['mpv', '--no-terminal', '--quiet', str(filepath)],
            ['mplayer', '-quiet', str(filepath)],
            ['vlc', '--intf', 'dummy', str(filepath)]
        ]

        for player_cmd in players:
            try:
                process = subprocess.Popen(
                    player_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
                self.state.set_process(process)
                self.state.needs_redraw = True
                return True
            except FileNotFoundError:
                continue

        return False

    def stop_playback(self):
        """Stop current playback"""
        process = self.state.get_process()
        if process:
            try:
                process.terminate()
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
            finally:
                self.state.set_process(None)
                self.state.needs_redraw = True

    def draw_box_with_title(self, y: int, x: int, height: int, width: int, title: str = ""):
        """Draw a box with optional title (nmtui style)"""
        try:
            # Draw corners
            self.stdscr.addch(y, x, curses.ACS_ULCORNER)
            self.stdscr.addch(y, x + width - 1, curses.ACS_URCORNER)
            self.stdscr.addch(y + height - 1, x, curses.ACS_LLCORNER)
            self.stdscr.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)

            # Draw horizontal lines
            for i in range(1, width - 1):
                self.stdscr.addch(y, x + i, curses.ACS_HLINE)
                self.stdscr.addch(y + height - 1, x + i, curses.ACS_HLINE)

            # Draw vertical lines
            for i in range(1, height - 1):
                self.stdscr.addch(y + i, x, curses.ACS_VLINE)
                self.stdscr.addch(y + i, x + width - 1, curses.ACS_VLINE)

            # Add title if provided
            if title:
                title_text = f"[ {title} ]"
                title_x = x + (width - len(title_text)) // 2
                if title_x > x and title_x + len(title_text) < x + width:
                    self.stdscr.addstr(y, title_x, title_text)
        except curses.error:
            pass  # Ignore drawing errors for small terminals

    def draw_button(self, y: int, x: int, text: str, selected: bool = False):
        """Draw button (nmtui style)"""
        try:
            button_text = f"< {text} >"
            if selected:
                self.stdscr.attron(curses.A_REVERSE)
                self.stdscr.addstr(y, x, button_text)
                self.stdscr.attroff(curses.A_REVERSE)
            else:
                self.stdscr.addstr(y, x, button_text)
        except curses.error:
            pass  # Ignore drawing errors

    def draw_interface(self):
        """Draw the nmtui-style interface"""
        if not self.state.needs_redraw:
            return

        term_y, term_x = self.stdscr.getmaxyx()
        self.stdscr.clear()

        # Main title (centered)
        main_title = "Terminal Music Player"
        title_x = (term_x - len(main_title)) // 2
        if title_x >= 0:
            try:
                self.stdscr.addstr(1, title_x, main_title)
            except curses.error:
                pass

        # Directory info
        dir_info = f"Directory: {self.directory}"
        if len(dir_info) > term_x - 4:
            dir_info = f"Directory: ...{str(self.directory)[-term_x+15:]}"
        try:
            self.stdscr.addstr(2, 2, dir_info[:term_x-3])
        except curses.error:
            pass

        # Draw main content box
        box_width = term_x - 4
        box_height = term_y - 7  # Account for directory line
        if box_width > 0 and box_height > 0:
            self.draw_box_with_title(4, 2, box_height, box_width, "Music Library")

        # Status line inside the box
        is_playing = self.state.get_process() is not None
        status = (f"Files: {len(self.files)} | Current: {self.highlight + 1} | "
                 f"Shuffle: {'ON' if self.shuffle_mode else 'OFF'} | "
                 f"Playing: {'YES' if is_playing else 'NO'}")

        if len(status) < box_width - 4:
            try:
                self.stdscr.addstr(5, 4, status)
            except curses.error:
                pass

        # Separator line
        if box_width > 4:
            try:
                for i in range(4, min(box_width - 2, term_x - 4)):
                    self.stdscr.addch(6, i + 2, curses.ACS_HLINE)
                self.stdscr.addch(6, 2, curses.ACS_LTEE)
                if box_width + 1 < term_x:
                    self.stdscr.addch(6, box_width + 1, curses.ACS_RTEE)
            except curses.error:
                pass

        # File list area
        list_start_y = 7
        list_height = box_height - 6
        display_count = max(1, list_height)

        for i in range(display_count):
            file_idx = self.start_index + i
            if file_idx >= len(self.files):
                break

            y_pos = list_start_y + i
            if y_pos >= term_y - 3:
                break

            # Truncate filename to fit
            max_name_len = max(10, box_width - 10)
            filename = self.files[file_idx]
            if len(filename) > max_name_len:
                display_name = filename[:max_name_len - 3] + "..."
            else:
                display_name = filename

            try:
                if self.highlight == file_idx:
                    # Highlighted selection
                    self.stdscr.attron(curses.A_REVERSE)
                    line_text = f" * {display_name}"
                    # Fill the rest of the line with spaces
                    padding = " " * max(0, box_width - 6 - len(line_text))
                    self.stdscr.addstr(y_pos, 4, (line_text + padding)[:term_x-5])
                    self.stdscr.attroff(curses.A_REVERSE)
                else:
                    line_text = f"   {display_name}"
                    self.stdscr.addstr(y_pos, 4, line_text[:term_x-5])
            except curses.error:
                pass

        # Bottom control buttons
        if term_y > 3:
            button_y = term_y - 3
            button_spacing = 12
            start_x = 4

            buttons = [
                ("Play", False),
                ("Stop", False),
                ("Shuffle", self.shuffle_mode),
                ("Random", False),
                ("Quit", False)
            ]

            for i, (text, selected) in enumerate(buttons):
                x_pos = start_x + button_spacing * i
                if x_pos + len(text) + 4 < term_x:
                    self.draw_button(button_y, x_pos, text, selected)

        # Help text at bottom
        if term_y > 1:
            help_text = "Use arrow keys to navigate, ENTER to play, SPACE to stop, 's' for shuffle, 'q' to quit"
            if len(help_text) < term_x - 2:
                try:
                    self.stdscr.addstr(term_y - 1, 2, help_text[:term_x - 3])
                except curses.error:
                    pass

        try:
            self.stdscr.refresh()
        except curses.error:
            pass
        self.state.needs_redraw = False

    def update_scroll(self, display_count: int):
        """Update scroll position"""
        if self.highlight < self.start_index:
            self.start_index = self.highlight
        elif self.highlight >= self.start_index + display_count:
            self.start_index = self.highlight - display_count + 1

        self.start_index = max(0, self.start_index)

    def play_random_file(self, display_count: int):
        """Play random file"""
        if not self.files:
            return

        random_index = random.randint(0, len(self.files) - 1)
        self.play_file(self.files[random_index])
        self.highlight = random_index
        self.update_scroll(display_count)
        self.state.needs_redraw = True

    def run(self, stdscr):
        """Main application loop"""
        self.stdscr = stdscr

        # Load media files
        try:
            file_count = self.load_media_files()
            if file_count == 0:
                return f"No media files found in directory: {self.directory}"
        except (OSError, PermissionError) as e:
            return f"Error accessing directory: {e}"

        # Configure curses
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.nodelay(True)

        random.seed()

        # Main event loop
        while True:
            term_y, term_x = stdscr.getmaxyx()
            display_count = max(1, term_y - 13)  # Account for directory line

            self.draw_interface()

            # Handle child process completion
            if self.state.child_finished:
                self.state.child_finished = False
                if self.shuffle_mode:
                    self.play_random_file(display_count)

            # Handle user input
            try:
                ch = stdscr.getch()
                if ch != curses.ERR:
                    self.state.needs_redraw = True

                    if ch == curses.KEY_UP:
                        if self.highlight > 0:
                            self.highlight -= 1
                            self.update_scroll(display_count)

                    elif ch == curses.KEY_DOWN:
                        if self.highlight < len(self.files) - 1:
                            self.highlight += 1
                            self.update_scroll(display_count)

                    elif ch == curses.KEY_PPAGE:  # Page Up
                        self.highlight = max(0, self.highlight - display_count)
                        self.update_scroll(display_count)

                    elif ch == curses.KEY_NPAGE:  # Page Down
                        self.highlight = min(len(self.files) - 1, self.highlight + display_count)
                        self.update_scroll(display_count)

                    elif ch == curses.KEY_HOME:
                        self.highlight = 0
                        self.start_index = 0

                    elif ch == curses.KEY_END:
                        self.highlight = len(self.files) - 1
                        self.update_scroll(display_count)

                    elif ch in (10, 13):  # Enter
                        self.shuffle_mode = False
                        if self.files:
                            self.play_file(self.files[self.highlight])

                    elif ch == ord(' '):  # Space to stop
                        self.stop_playback()

                    elif ch in (ord('s'), ord('S')):  # Toggle shuffle
                        self.shuffle_mode = not self.shuffle_mode
                        if self.shuffle_mode and not self.state.get_process():
                            self.play_random_file(display_count)

                    elif ch in (ord('r'), ord('R')):  # Random play
                        self.play_random_file(display_count)

                    elif ch in (ord('q'), ord('Q'), 27):  # Quit
                        break

                    else:
                        self.state.needs_redraw = False

            except KeyboardInterrupt:
                break

            time.sleep(REFRESH_DELAY)

        # Cleanup
        self.stop_playback()
        return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Terminal Music Player - A curses-based media player',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Play files from current directory
  %(prog)s /path/to/music     # Play files from specific directory
  %(prog)s ~/Music            # Play files from home music directory
  %(prog)s "My Music Folder"  # Play files from directory with spaces

Supported formats: mp3, flac, wav, ogg, m4a, aac, wma, opus, mp4, avi, mkv, mov, webm

Controls:
  ↑/↓         Navigate files
  PgUp/PgDn   Page up/down
  Home/End    Go to first/last file
  Enter       Play selected file
  Space       Stop playback
  s           Toggle shuffle mode
  r           Play random file
  q/Esc       Quit

Requires: mpv, mplayer, or vlc media player
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory containing media files (default: current directory)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Terminal Music Player 2.0'
    )

    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()

    # Validate directory
    directory_path = Path(args.directory)

    if not directory_path.exists():
        print(f"Error: Directory does not exist: {directory_path}")
        return 1

    if not directory_path.is_dir():
        print(f"Error: Path is not a directory: {directory_path}")
        return 1

    # Check if directory is accessible
    try:
        list(directory_path.iterdir())
    except PermissionError:
        print(f"Error: Permission denied accessing directory: {directory_path}")
        return 1
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return 1

    player = MediaPlayer(str(directory_path))

    try:
        result = curses.wrapper(player.run)
        if result:
            print(result)
            print("Supported formats: mp3, flac, wav, ogg, m4a, aac, wma, opus, mp4, avi, mkv, mov, webm")
            print("Requires: mpv, mplayer, or vlc media player")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
