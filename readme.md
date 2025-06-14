exe file :- 

python -m PyInstaller --onefile --noconsole --icon=assets/favicon.ico --add-data "assets;assets" --add-data "config;config" --add-data "haar;haar" --add-data "modules;modules" --add-data "ui;ui" main.py
