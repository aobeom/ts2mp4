@echo off
REM usage: ts2mp4.py [-h] --input VIDEO --size SIZE --params PARAMS --vmode {1,2}
REM              --amode {1,2,3} [--bitrate BITRATE] [--vfr] [--degrain]
REM              [--upscale] [--double | --ivtc]

REM Any video convert to AVC / HEVC

REM optional arguments:
REM  -h, --help         show this help message and exit
REM  --input VIDEO      Input video source
REM  --size SIZE        display resolution (width)x(heigh)
REM  --params PARAMS    x26x params file
REM  --vmode {1,2}      Video Encoder [1:x264 / 2:x265]
REM  --amode {1,2,3}    Audio Encoder [1:fdkaac / 2:flac / 3:ffmpeg]
REM  --bitrate BITRATE  Audio Bitrate [amode=3]
REM  --vfr              VFR video
REM  --degrain          RemoveGrainSSE3
REM  --upscale          Upscale video
REM  --double           QTGMC deint mode and 60 FPS
REM  --ivtc             IVTC deint mode and 24 FPS

set input=%~1
python %~dp0ts2mp4.py --input %input% --params %~dp0configs\x264-paramas.txt --size 1920x1080 --vmode 1 --amode 1 --degrain

pause