# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

SP = r'C:\Users\natra\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages'

_mpl_datas = []
_mpl_bins = []
_mpl_hidden = []

datas = _mpl_datas + [
    ('hand_landmarker.task', '.'),
    (SP + r'\mediapipe', 'mediapipe'),
    (SP + r'\spellchecker', 'spellchecker'),
    (SP + r'\cv2', 'cv2'),
    (SP + r'\google\generativeai', 'google/generativeai'),
    (SP + r'\google\ai', 'google/ai'),
    (SP + r'\certifi', 'certifi'),
]

binaries = _mpl_bins + [
    (SP + r'\mediapipe\tasks\c\libmediapipe.dll', 'mediapipe/tasks/c'),
    (SP + r'\cv2\opencv_videoio_ffmpeg4130_64.dll', 'cv2'),
]

hiddenimports = _mpl_hidden + [
    'mediapipe', 'mediapipe.tasks', 'mediapipe.tasks.python', 'mediapipe.tasks.python.vision',
    'mediapipe.tasks.python.core', 'mediapipe.tasks.python.components', 'mediapipe.tasks.python.audio',
    'mediapipe.tasks.python.text', 'mediapipe.tasks.metadata', 'google.generativeai',
    'google.ai.generativelanguage_v1beta', 'google.api_core', 'google.api_core.gapic_v1',
    'google.auth', 'google.auth.transport', 'google.auth.transport.requests', 'google.protobuf',
    'grpc', 'cv2', 'pyautogui', 'spellchecker', 'threading', 'certifi', 'pyi_splash',
]

a = Analysis(
    ['test.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook_stub_matplotlib.py'],
    excludes=[
        'sklearn', 'scipy', 'nltk', 'transformers', 'torch', 'tensorflow', 'jax',
        'IPython', 'jupyter', 'pandas', 'sympy', 'wx', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
    ],
    noarchive=False,
    optimize=0,
)

# NATIVE SPLASH SCREEN (shows up INSTANTLY while extraction happens)
splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.datas,
    [],
    name='AirType',
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
)
