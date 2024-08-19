# -*- mode: python -*-

block_cipher = None

a = Analysis(
    ['Level-Creator.py'],
    pathex=['Users/JaiEs/OneDrive/Documents/VS/Pygame/aguhghg/build'],
    binaries=[],
    datas=[
        ('tiles/', 'tiles/'),  # Include folders
        ('modules/', 'modules/'),
        ('levels/', 'levels/')
        ('graphics/, 'graphics/')
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Level Creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Level Creator',
)
