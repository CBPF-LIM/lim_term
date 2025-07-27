# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LimTerm Windows executable
Auto-builds via GitHub Actions on release tags
"""

block_cipher = None

# Data files to include in the executable
added_files = [
    ('limterm/languages/*.yml', 'limterm/languages'),
    ('limterm/config.py', 'limterm'),
]

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'limterm.gui.main_window',
    'limterm.gui.config_tab',
    'limterm.gui.data_tab', 
    'limterm.gui.graph_tab',
    'limterm.core.graph_manager',
    'limterm.core.serial_manager',
    'limterm.i18n.language_manager',
    'limterm.i18n.config_manager',
    'limterm.utils.file_utils',
    'limterm.utils.serial_utils',
    'limterm.utils.mock_serial',
    'yaml',
    'matplotlib.backends.backend_tkagg',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.ttk',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
]

a = Analysis(
    ['limterm/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LimTerm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here later: icon='icon.ico'
    version=None,
)
