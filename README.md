# ts2mp4

## 参数说明

```python
usage: ts2mp4.py [-h] -i VIDEO [-t TRIM] [-f] [-a ATYPE] -m MODE [-b ABITRATE]
                 [-d] [-s RES] -c CONFIG

Any video convert to AVC / HEVC

optional arguments:
  -h, --help  show this help message and exit
  -i VIDEO    input source | 输入视频[必填]
  -t TRIM     trim start,end | 按帧数切割视频，对音频无效，仅调试用
  -f          60 FPS | 布尔型，带上参数即输出60帧
  -a ATYPE    Type [1:fdkaac / 2:ffmpeg]
  -m MODE     Mode [1:x264 / 2:x265] | x26x选择[必填]
  -b ABITRATE Audio bitrate 128, 144, 192[default copy]
  -d          deinterlacing switch | vfr视频适用
  -s RES      display resolution [default: 1920x1080] | 分辨率设置
  -c CONFIG   x26x params file | x26x参数文件
```

x264 ffmpeg-aac:  
ts2mp4.py -i input.video -c x264-paramas.txt -m 1

x265 ffmpeg-aac:  
ts2mp4.py -i input.video -c x265-paramas.txt -m 2

x264 60fps ffmpeg-aac 192k:  
ts2mp4.py -i input.video -c x264-paramas.txt -m 1 -f -a 2 -b 192

x264 60fps fdkaac:  
ts2mp4.py -i input.video -c x264-paramas.txt -m 1 -f -a 1

输出到同目录下的input_muxed.mp4

## 使用说明

默认参数  
- 反交错 / QTGMC(preset="fast",fpsdivisor=2)
- 音频 / Fdkaac VBR=5 | ffmpeg-aac cbr

若需要压制字幕，则把字幕文件放在视频目录下，名字与视频相同

## 执行环境

plugins:
- LSMASHSource.dll  
- mt_masktools-26.dll  
- mvtools2.dll
- nnedi3.dll
- QTGMC-3.32.avsi
- RemoveGrainSSE3.dll
- VSFilterMod32.dll

exec:
- mp4box
- avs4x26x.exe
- fdkaac.exe
- ffmpeg.exe
- x264.exe
- x265.exe

# videoconcat

## 使用说明

将视频用数字依次编号，然后在该目录执行videoconcat.py自动合成，最终输出all.mp4

