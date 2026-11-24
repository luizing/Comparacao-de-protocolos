@echo off
rem Atalho: dois cliques aqui sobem todos os servidores e o frontend.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0rodar-tudo.ps1" %*
pause
