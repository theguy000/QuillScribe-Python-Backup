#!/usr/bin/env python3
"""
QuillScribe Application Runner
Launch the beautiful voice-to-text transcription app
"""

import sys
import os
import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)
if getattr(sys, 'frozen', False):
    pass
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from quillscribe.main import main

if __name__ == "__main__":
    sys.exit(main())