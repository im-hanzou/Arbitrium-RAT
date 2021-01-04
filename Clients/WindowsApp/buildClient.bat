@echo off
pyinstaller --onefile runFrame.py
copy Client_tools\toolbox.exe dist\
copy Client_tools\SFXAutoInstaller.conf dist\
copy Client_tools\start_script.vbs dist\
cd dist
"C:\Program Files\WinRAR\Rar.exe" a -r -cfg -sfx -z"SFXAutoInstaller.conf" Standalone.exe