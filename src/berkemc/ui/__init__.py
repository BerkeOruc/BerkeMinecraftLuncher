"""
User Interface components with keyboard navigation
"""

import os
import sys
from typing import List, Dict, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt

class MenuItem:
    """Menu item with callback function"""
    def __init__(self, key: str, label: str, description: str = "", callback: Callable = None, color: str = "white"):
        self.key = key
        self.label = label
        self.description = description
        self.callback = callback
        self.color = color

class KeyboardNavigator:
    """Keyboard navigation system for menus - Cross-platform compatible"""
    
    def __init__(self, console: Console):
        self.console = console
        self.current_index = 0
        self.items = []
        self.running = True
        
    def add_item(self, item: MenuItem):
        """Add menu item"""
        self.items.append(item)
        
    def _get_key(self):
        """Get single key press - Linux compatible with arrow key support"""
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                
                # Read first character
                ch = sys.stdin.read(1)
                
                # Check for escape sequence (arrow keys)
                if ch == '\x1b':
                    # Read next two characters
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':  # Up arrow
                            return 'UP'
                        elif ch3 == 'B':  # Down arrow
                            return 'DOWN'
                        elif ch3 == 'C':  # Right arrow
                            return 'RIGHT'
                        elif ch3 == 'D':  # Left arrow
                            return 'LEFT'
                
                # Check for special keys
                if ch == '\r' or ch == '\n':
                    return 'ENTER'
                elif ch == '\x1b':  # ESC
                    return 'ESC'
                elif ch == '\x7f':  # Backspace
                    return 'BACKSPACE'
                elif ch == '\x03':  # Ctrl+C
                    return 'CTRL_C'
                
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except ImportError:
            # Fallback to input if termios not available
            return input().strip()
        
    def show_menu(self, title: str, items: List[MenuItem], show_exit: bool = True) -> Optional[str]:
        """Show interactive menu with keyboard navigation"""
        self.items = items
        self.current_index = 0
        self.running = True
        
        if show_exit:
            self.items.append(MenuItem("0", "Çıkış", "Menüden çık", color="red"))
            
        while self.running:
            os.system('clear')
            
            # Create menu table
            table = Table(
                show_header=False,
                box=None,
                padding=(0, 2),
                expand=True
            )
            table.add_column("", style="bold cyan", width=3, justify="center")
            table.add_column("", style="white", width=25)
            table.add_column("", style="dim", width=35)
            
            # Add items to table
            for i, item in enumerate(self.items):
                if i == self.current_index:
                    # Highlight current item
                    table.add_row(
                        f"[bold yellow]▶[/bold yellow]",
                        f"[bold {item.color}]{item.label}[/bold {item.color}]",
                        f"[bold dim]{item.description}[/bold dim]"
                    )
                else:
                    table.add_row(
                        f"[bold cyan]{item.key}[/bold cyan]",
                        f"[{item.color}]{item.label}[/{item.color}]",
                        f"[dim]{item.description}[/dim]"
                    )
            
            # Show menu
            panel = Panel(
                table,
                title=f"[bold white]═══ {title} ═══[/bold white]",
                border_style="bright_cyan",
                padding=(1, 2),
                expand=False
            )
            
            self.console.print(panel)
            self.console.print("\n[yellow]↑↓[/yellow] Seç | [green]Enter[/green] Onayla | [red]Esc[/red] Çık")
            
            # Handle keyboard input
            try:
                # Wait for key press
                key = self._get_key()
                
                if key == 'ESC':  # ESC key
                    return None
                elif key == 'ENTER':  # Enter key
                    selected_item = self.items[self.current_index]
                    if selected_item.callback:
                        result = selected_item.callback()
                        if result is not None:
                            return result
                    else:
                        return selected_item.key
                elif key == 'UP' or key == 'w':  # Up arrow or W
                    self.current_index = (self.current_index - 1) % len(self.items)
                elif key == 'DOWN' or key == 's':  # Down arrow or S
                    self.current_index = (self.current_index + 1) % len(self.items)
                elif key == 'CTRL_C':  # Ctrl+C
                    return None
                elif key.isdigit():
                    # Direct number selection
                    num = int(key)
                    if 1 <= num <= len(self.items):
                        self.current_index = num - 1
                        selected_item = self.items[self.current_index]
                        if selected_item.callback:
                            result = selected_item.callback()
                            if result is not None:
                                return result
                        else:
                            return selected_item.key
                            
            except KeyboardInterrupt:
                return None
            except Exception as e:
                self.console.print(f"[red]Hata: {e}[/red]")
                
        return None

class ColorManager:
    """Color management system to fix display issues"""
    
    @staticmethod
    def format_text(text: str, color: str = "white", style: str = "") -> str:
        """Format text with proper color codes - fixes display issues"""
        if not text:
            return ""
            
        # Remove any existing color codes to prevent conflicts
        import re
        text = re.sub(r'\[[^\]]*\]', '', text)
        
        # Ensure proper color formatting
        if style and color:
            return f"[{style} {color}]{text}[/{style} {color}]"
        elif color:
            return f"[{color}]{text}[/{color}]"
        else:
            return text
    
    @staticmethod
    def create_colored_panel(content: str, title: str = "", border_style: str = "cyan") -> Panel:
        """Create properly colored panel"""
        return Panel(
            content,
            title=f"[bold white]{title}[/bold white]" if title else None,
            border_style=border_style,
            padding=(1, 2),
            expand=False
        )

class ProgressDisplay:
    """Enhanced progress display with better formatting"""
    
    def __init__(self, console: Console):
        self.console = console
        
    def show_progress(self, current: int, total: int, description: str = "İşleniyor"):
        """Show progress with proper formatting"""
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * current // total) if total > 0 else 0
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        self.console.print(f"\r[cyan]{description}[/cyan] [{bar}] {percentage:.1f}%", end="")
        
        if current >= total:
            self.console.print()  # New line when complete

__all__ = [
    'MenuItem',
    'KeyboardNavigator', 
    'ColorManager',
    'ProgressDisplay'
]
