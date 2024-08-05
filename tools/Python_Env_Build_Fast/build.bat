@echo on
python -m  nuitka --onefile --standalone --lto=yes --remove-output --show-progress --show-memory --assume-yes-for-downloads .\run.py