# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Get the current directory
current_dir = os.path.dirname(os.path.abspath('run.py'))

# Collect data files
datas = [
    (os.path.join(current_dir, 'src', 'quillscribe', 'icons'), 'icons'),
    (os.path.join(current_dir, 'src', 'sounds'), 'sounds'),
]

a = Analysis(
    ['run.py'],
    pathex=[os.path.join(current_dir, 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'torch', 'torchvision', 'torchaudio',  # Exclude PyTorch
        'tensorflow', 'keras',  # Exclude TensorFlow
        'matplotlib', 'scipy',  # Exclude heavy scientific packages
        'pandas',  # Exclude pandas
        'tkinter',  # Exclude tkinter
        'test', 'tests', 'unittest',  # Exclude test modules
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='QuillScribe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(current_dir, 'src', 'quillscribe', 'icons', 'app_logo.ico'),
)
