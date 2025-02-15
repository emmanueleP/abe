import os
import shutil
import subprocess
from datetime import datetime

def build_windows():
    print("🚀 Inizia il build per Windows...")
    
    # Pulisci le directory di build e dist
    for dir in ['build', 'dist']:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    
    # Crea l'eseguibile con PyInstaller
    subprocess.run(['pyinstaller', 'abe.spec'], check=True)
    
    # Crea l'installer con Inno Setup
    subprocess.run(['iscc', 'setup.iss'], check=True)
    
    # Sposta l'installer nella cartella releases
    release_dir = 'releases'
    os.makedirs(release_dir, exist_ok=True)
    
    version = "1.0.5"
    date = datetime.now().strftime("%Y%m%d")
    installer_name = f"Abe-Gestionale_{version}_win_{date}.exe"
    
    shutil.move(
        os.path.join('installer', 'Abe-Gestionale_Setup.exe'),
        os.path.join(release_dir, installer_name)
    )
    
    print(f"✅ Build completato: {installer_name}")

if __name__ == '__main__':
    build_windows() 