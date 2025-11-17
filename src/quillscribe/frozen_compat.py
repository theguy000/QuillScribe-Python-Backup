"""
Frozen Executable Compatibility Module
Provides unified resource path detection for Nuitka (PyInstaller support maintained for compatibility)
"""

import sys
import os
from pathlib import Path
from typing import Union, Optional


def get_base_path() -> Optional[Path]:
    """
    Get the base path for resources in a frozen executable.
    
    Supports both PyInstaller and Nuitka frozen executables:
    - PyInstaller: Uses sys._MEIPASS (temporary extraction directory)
    - Nuitka onefile: Uses the onefile temp extraction directory
    - Nuitka standalone: Uses directory containing the executable
    
    Returns:
        Path: Base directory containing bundled resources, or None if not frozen
    """
    if getattr(sys, 'frozen', False):
        # Running as frozen executable
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller extracts to temp directory
            return Path(sys._MEIPASS)
        else:
            # Nuitka: Check for onefile mode first
            # In Nuitka onefile, resources are in the same directory as the running module
            # Try to find the extracted directory by checking where this module is
            try:
                # Get the directory of the current module
                if __file__:
                    module_dir = Path(__file__).parent.resolve()
                    # In onefile mode, resources are extracted alongside the .pyz package
                    # Go up to the extraction root
                    current = module_dir
                    for _ in range(3):  # Try up to 3 levels up
                        if (current / 'icons').exists():
                            return current
                        current = current.parent
            except (NameError, AttributeError):
                pass
            
            # Fallback: Use the directory containing sys.executable
            if hasattr(sys, 'executable'):
                exec_dir = Path(sys.executable).parent
                # For onefile, check if resources are in a temp subdir
                if (exec_dir / 'icons').exists():
                    return exec_dir
                # Check common Nuitka temp patterns
                import tempfile
                temp_base = Path(tempfile.gettempdir())
                for temp_dir in temp_base.glob('onefile_*'):
                    if (temp_dir / 'icons').exists():
                        return temp_dir
                return exec_dir
            else:
                return Path(os.path.dirname(sys.argv[0]))
    else:
        # Running from source - return None to signal development mode
        return None


def get_resource_path(relative_path: Union[str, Path], dev_base: Optional[Path] = None) -> Path:
    """
    Get the full path to a bundled resource file.
    
    Args:
        relative_path: Relative path to the resource (e.g., 'icons/app_logo.ico')
        dev_base: Base path to use in development mode (defaults to src/quillscribe)
        
    Returns:
        Path: Full path to the resource
    """
    base_path = get_base_path()
    
    if base_path is not None:
        # Frozen executable mode
        return base_path / relative_path
    else:
        # Development mode
        if dev_base is None:
            # Default to src/quillscribe directory
            dev_base = Path(__file__).parent
        return dev_base / relative_path


def is_frozen() -> bool:
    """
    Check if running as a frozen executable.
    
    Returns:
        bool: True if running as frozen executable, False if running from source
    """
    return getattr(sys, 'frozen', False)
