import os
import shutil
import subprocess
from datetime import datetime

def build_macos():
    print("🚀 Inizia il build per macOS...")
    
    # Pulisci le directory di build e dist
    for dir in ['build', 'dist']:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    
    # Crea l'app bundle con PyInstaller
    subprocess.run(['pyinstaller', 'abe.spec'], check=True)
    
    # Crea il DMG
    app_path = 'dist/Abe-Gestionale.app'
    version = "1.0.5"
    date = datetime.now().strftime("%Y%m%d")
    dmg_name = f"Abe-Gestionale_{version}_macos_{date}.dmg"
    
    # Crea la directory releases
    release_dir = 'releases'
    os.makedirs(release_dir, exist_ok=True)
    
    # Crea il DMG usando create-dmg
    subprocess.run([
        'create-dmg',
        '--volname', 'Abe-Gestionale',
        '--volicon', 'src/assets/logo_abe.icns',
        '--window-pos', '200', '120',
        '--window-size', '800', '400',
        '--icon-size', '100',
        '--icon', 'Abe-Gestionale.app', '200', '200',
        '--app-drop-link', '600', '200',
        '--background', 'src/assets/dmg_background.png',
        '--text-size', '14',
        '--add-file', 'README.md', '200', '300',
        os.path.join(release_dir, dmg_name),
        app_path
    ], check=True)
    
    print(f"✅ Build completato: {dmg_name}")

if __name__ == '__main__':
    build_macos() 