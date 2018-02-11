@echo off
set input=%~1
python %~dp0ts2mp4.py -i %input% -c %~dp0configs\x264-paramas.txt -m 1 -s 1920x1080
pause