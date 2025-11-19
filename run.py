#!/usr/bin/env python3
"""
QuillScribe Application Runner
Launch the beautiful voice-to-text transcription app
"""

import sys
import os
import warnings

# Suppress the pkg_resources deprecation warning from ctranslate2
warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)

# Handle both development and frozen executable environments
if getattr(sys, 'frozen', False):
    # Running as frozen executable (Nuitka)
    # Nuitka includes quillscribe package directly, no path modification needed
    pass
else:
    # Running from source
    # Add src directory to path (append to avoid shadowing standard libraries)
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from quillscribe.main import main

if __name__ == "__main__":
    sys.exit(main())