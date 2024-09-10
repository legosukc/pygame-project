# -*- mode: python -*-

block_cipher = None

main = Analysis(
    ['main.py'],
    pathex=['./'],
    binaries=[],
    datas=[
        ('res/', 'res/'),
        ('tools/', 'tools/'),
        ('map/', 'map/'),
        ('snd/', 'snd/')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)

creator = Analysis(
    ['Level-Creator.py'],
    pathex=['./'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)

mainpyz = PYZ(main.pure, main.zipped_data, cipher=block_cipher)
creatorpyz = PYZ(creator.pure, creator.zipped_data, cipher=block_cipher)

mainexe = EXE(
    mainpyz,
    main.scripts,
    [],
    exclude_binaries=True,
    name='Game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

creatorexe = EXE(
    creatorpyz,
    creator.scripts,
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
    mainexe,
    creatorexe,
    main.binaries,
    main.zipfiles,
    main.datas,
    creator.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='game',
)