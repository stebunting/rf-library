@echo off
del /f /q /s dist > NUL
del /f /q /s build > NUL
rmdir /s /q dist
rmdir /s /q build

pyinstaller -w rf-library-win.spec