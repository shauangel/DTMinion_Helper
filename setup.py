from setuptools import setup
import os
import ctypes.util


libffi_path = "/opt/homebrew/Cellar/libffi/3.4.8/lib/libffi.8.dylib"
print("💡 libffi path:", libffi_path)

APP = ['desktop_pet.py']
DATA_FILES = [
    ('GIF', [f'GIF/{f}' for f in os.listdir('GIF') if f.endswith('.gif')]),
    ('images', ['images/bg.png', 'images/icon.png']),
    ('', ['lines.json', 'diagram_bubble.py']),
]
OPTIONS = {
    'argv_emulation': False,
    'includes': ['ctypes', 'PyQt5'],
    'packages': ['PyQt5'],
    'frameworks': [libffi_path] if libffi_path else [],
    'plist': {
        'CFBundleName': 'DesktopPet',
        'LSUIElement': True  # change to True after it's working
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
