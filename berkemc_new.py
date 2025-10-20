#!/usr/bin/env python3
"""
BerkeMC - Advanced Minecraft Launcher
Enhanced version with keyboard navigation and professional structure
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from berkemc.core.launcher import main

if __name__ == "__main__":
    main()
