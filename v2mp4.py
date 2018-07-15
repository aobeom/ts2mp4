# coding=utf8
import os
import argparse

workdir = os.path.dirname(os.path.abspath(__file__))


class v2mp4(object):
    def __init__(self):
        self.plugin_path = os.path.join(workdir, "plugins")

    def show_plugin(self):
        plugins = os.listdir(self.plugin_path)
        return plugins

    def create_avs(self, source, resize, vfr=False, degrain=False, upscale=False, double_fps=False, ivtc=False):
        source_path = os.path.splitext(source)[0]
        avs_name = source_path + ".avs"
        with open(avs_name, "wb") as f:
            # 载入滤镜
            for plugin in self.show_plugin():
                plugin_ext = os.path.splitext(plugin)[-1]
                plugin_name = os.path.join(self.plugin_path, plugin)
                if plugin_ext == ".dll":
                    plugin_load = 'LoadPlugin("{}")\r\n'.format(plugin_name)
                elif plugin_ext == ".avsi":
                    plugin_load = 'Import("{}")\r\n'.format(plugin_name)
                f.write(plugin_load)
            # 导入视频
            avs_video = 'LWLibavVideoSource("{}")\r\n'
            if vfr:
                avs_video = 'LWLibavVideoSource("{}",repeat=true)\r\n'
            f.write(avs_video.format(source))
            # 设定分辨率
            avs_res = 'LanczosResize({})\r\n'.format(resize.replace("x", ","))
            if upscale:
                avs_res = 'nnedi3_resize16({})\r\n'.format(
                    resize.replace("x", ","))
            # 反交错模式 5烂2/帧帧烂 和double_fps互斥
            if ivtc:
                # 1: 24 FPS 3:30 FPS
                avs_deint = 'tfm().tdecimate(hybrid=1)'
            else:
                avs_deint = 'QTGMC(preset="fast",fpsdivisor=2)\r\n'
            if double_fps:
                avs_deint = 'QTGMC(preset="fast",fpsdivisor=1,ShutterBlur=1,ShutterAngleSrc=0,ShutterAngleOut=720)\r\n'
            f.write(avs_deint)
            f.write(avs_res)
            # 降噪
            if degrain:
                avs_grain = 'RemoveGrainSSE3_RemoveGrain(3,3)\r\n'
                f.write(avs_grain)
            # 封装字幕
            subtitle = source_path + ".ass"
            if os.path.exists(subtitle):
                avs_ass = 'TextSubMod("{}")\r\n'.format(subtitle)
                f.write(avs_ass)
        return avs_name

    def audio_encode(self, source, ffmpeg, audio_exec=None, mode=None, bitrate=None):
        # fdkaac
        if mode == 1:
            output = os.path.splitext(source)[0] + ".m4a"
            wav2audio = "{ffmpeg} -i {source} -vn -f wav - | {audio_exec} - -m 5 --ignorelength -o {output}".format(
                ffmpeg=ffmpeg, source=source, audio_exec=audio_exec, output=output)
        # flac
        elif mode == 2:
            output = os.path.splitext(source)[0] + ".flac"
            wav2audio = "{ffmpeg} -i {source} -vn -f wav - | {audio_exec} -f - -5 --ignore-chunk-sizes -o {output}".format(
                ffmpeg=ffmpeg, source=source, audio_exec=audio_exec, output=output)
        # ffmpeg aac
        else:
            output = os.path.splitext(source)[0] + ".m4a"
            if bitrate:
                bitrate = "aac -ab {}k".format(bitrate)
            else:
                bitrate = "copy"
            wav2audio = "{ffmpeg} -i {source} -vn -acodec {bitrate} {output} -y".format(
                ffmpeg=ffmpeg, source=source, bitrate=bitrate, output=output)
        os.system(wav2audio)
        return output

    def video_encode(self, source, params, avs4x26x, x26x):
        with open(params, "r") as f:
            command = f.read()
            if "x264" in x26x:
                ext = ".264"
            elif "x265" in x26x:
                ext = ".hevc"
            output = os.path.splitext(source)[0] + ext
            cmd = "{avs4x26x} --x265-binary {x26x} {source} {command} --output {output}".format(
                avs4x26x=avs4x26x, x26x=x26x, source=source, command=command, output=output)
        os.system(cmd)
        return output

    def merge(self, merge_exec, video, audio, mp4=True):
        # mp4box
        if mp4:
            output = os.path.splitext(video)[0] + "_muxed.mp4"
            merge = "{merge_exec} -add {video}#video -add {audio}#audio -new {output}".format(
                merge_exec=merge_exec, video=video, audio=audio, output=output)
            os.system(merge)
            print(merge)
        # mkv
        else:
            output = os.path.splitext(video)[0] + "_muxed.mkv"
            merge = "{merge_exec} -o {output} {video} --language 0:jpn {audio}".format(
                merge_exec=merge_exec, video=video, audio=audio, output=output)
            os.system(merge)


def opt():
    parser = argparse.ArgumentParser(
        description="Any video convert to AVC / HEVC")
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('--input', dest='video',
                        help='Input video source', required=True)
    parser.add_argument('--size', dest='size',
                        help='display resolution (width)x(heigh)', required=True)
    parser.add_argument('--params', dest='params',
                        help='x26x params file', required=True)
    parser.add_argument('--vmode', dest='vmode', type=int,
                        choices=[1, 2], help="Video Encoder [1:x264 / 2:x265]", required=True)
    parser.add_argument('--amode', dest='amode', type=int, choices=[
                        1, 2, 3], default=None, help="Audio Encoder [1:fdkaac / 2:flac / 3:ffmpeg]", required=True)
    parser.add_argument('--bitrate', dest='bitrate',
                        default=None, help="Audio Bitrate [amode=3]")

    parser.add_argument('--vfr', dest='vfr', default=False,
                        action="store_true", help='VFR video')
    parser.add_argument('--degrain', dest='degrain', default=False,
                        action="store_true", help='RemoveGrainSSE3')
    parser.add_argument('--upscale', dest='upscale', default=False,
                        action="store_true", help='Upscale video')

    group.add_argument('--double', dest='double', default=False,
                       action="store_true", help="QTGMC deint mode and 60 FPS")
    group.add_argument('--ivtc', dest='ivtc', default=False,
                       action='store_true', help="IVTC deint mode and 24 FPS")

    args = parser.parse_args()
    return args


def main():
    args = opt()

    video = args.video
    size = args.size
    params = args.params
    vmode = args.vmode
    amode = args.amode
    bitrate = args.bitrate

    vfr = args.vfr
    degrain = args.degrain
    upscale = args.upscale

    double = args.double
    ivtc = args.ivtc

    exec_path = os.path.join(workdir, "exec")
    exec_avs = os.path.join(exec_path, "avs4x26x.exe")
    exec_ffmpeg = os.path.join(exec_path, "ffmpeg.exe")

    if vmode == 1:
        exec_x26x = os.path.join(exec_path, "x264.exe")
    elif vmode == 2:
        exec_x26x = os.path.join(exec_path, "x265.exe")

    mergeTool = os.path.join(exec_path, "mp4box", "mp4box.exe")
    if amode == 1:
        exec_audio = os.path.join(exec_path, "fdkaac.exe")
        mp4 = True
    elif amode == 2:
        exec_audio = os.path.join(exec_path, "flac.exe")
        mergeTool = os.path.join(exec_path, "mkvmerge.exe")
        mp4 = False
    elif amode == 3:
        exec_audio = None
        mp4 = True

    t = v2mp4()
    avs_file = t.create_avs(video, size, vfr, degrain, upscale, double, ivtc)
    audio_path = t.audio_encode(video, exec_ffmpeg, exec_audio, amode, bitrate)
    video_path = t.video_encode(avs_file, params, exec_avs, exec_x26x)
    t.merge(mergeTool, video_path, audio_path, mp4)


if __name__ == "__main__":
    main()
