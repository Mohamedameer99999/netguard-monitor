import PyInstaller.__main__
import sys, os, shutil
from pathlib import Path

NAME = 'NetGuard-Monitor'
DIST_DIR = Path(__file__).resolve().parent / 'dist'

if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)

FRONTEND = Path(__file__).resolve().parent / 'web' / 'frontend'

PyInstaller.__main__.run([
    'main.py',
    '--name', NAME,
    '--onefile',
    '--noconsole',
    '--add-data', f'{FRONTEND}{os.pathsep}web/frontend',
    '--hidden-import', 'psutil',
    '--collect-submodules', 'psutil',
    '--distpath', str(DIST_DIR),
    '--workpath', str(Path(__file__).resolve().parent / 'build'),
    '--specpath', str(Path(__file__).resolve().parent),
])

EXE = DIST_DIR / f'{NAME}.exe'
if EXE.exists():
    size = EXE.stat().st_size / (1024*1024)
    print(f'\n[OK] {NAME}.exe created ({size:.1f} MB)')
    print(f'     {EXE}')
else:
    print(f'\n[FAIL] Build failed')
