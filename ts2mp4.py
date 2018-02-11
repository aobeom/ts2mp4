import os
import sys
import argparse


class ts2mp4(object):
    def __init__(self, res, params, deint, fps, trim=None):
        self.res = res.replace("x", ",")
        self.params = params
        self.trim = trim
        self.deint = deint
        self.fps = fps
        self.dlls = [
            "LSMASHSource.dll",
            "mt_masktools-26.dll",
            "mvtools2.dll",
            "nnedi3.dll",
            "RemoveGrainSSE3.dll",
            "VSFilterMod32.dll",
            "QTGMC-3.32.avsi"
        ]

    def avsMethod(self, source):
        mainpath = os.path.splitext(source)[0]
        name = mainpath + ".avs"
        subtitle = mainpath + ".ass"
        dllfolder = os.path.join(sys.path[0], "plugins")
        f = open(name, "wb")
        if self.fps:
            fpsdivisor = 1
        else:
            fpsdivisor = 2
        for dll in self.dlls:
            dll_path = os.path.join(dllfolder, dll)
            ext = os.path.splitext(dll)[-1]
            if ext == ".dll":
                dll_load = 'LoadPlugin("{}")\r\n'.format(dll_path)
            elif ext == ".avsi":
                dll_load = 'Import("{}")\r\n'.format(dll_path)
            f.write(dll_load)
        if self.deint:
            avs_video = 'LWLibavVideoSource("{}",repeat=true)\r\n'.format(
                source)
        else:
            avs_video = 'LWLibavVideoSource("{}")\r\n'.format(source)
        avs_res = 'LanczosResize({})\r\n'.format(self.res)
        avs_grain = 'RemoveGrainSSE3_RemoveGrain(3,3)\r\n'
        avs_deint = 'QTGMC(preset="fast",fpsdivisor={})\r\n'.format(fpsdivisor)
        f.write(avs_video)
        f.write(avs_res)
        f.write(avs_grain)
        f.write(avs_deint)
        if self.trim:
            trim = self.trim
            avs_trim = 'trim({})\r\n'.format(trim)
            f.write(avs_trim)
        if os.path.exists(subtitle):
            avs_ass = 'TextSubMod("{}")\r\n'.format(subtitle)
            f.write(avs_ass)
        f.close()
        return name

    def audioMethod(self, prog1, prog2, source):
        output = os.path.splitext(source)[0] + ".m4a"
        wav2aac = "{vprog} -i {input} -vn -map 0:1 -f wav - | {aprog} - -m 5 --ignorelength -o {output}".format(
            vprog=prog1, input=source, aprog=prog2, output=output)
        os.system(wav2aac)
        return output

    def videoMethod(self, prog1, prog2, source, ext):
        output = os.path.splitext(source)[0] + ext
        f = open(self.params, "rb")
        command = f.read()
        hevc = "{prog1} --x265-binary {prog2} {input} {cmd} --output {output}".format(
            prog1=prog1, prog2=prog2, input=source, cmd=command, output=output)
        os.system(hevc)
        return output

    def mergeMethod(self, prog, video, audio):
        output = os.path.splitext(video)[0] + "_muxed.mp4"
        merge = "{vprog} -add {video}#video -add {audio}#audio -new {output}".format(
            vprog=prog, video=video, audio=audio, output=output)
        os.system(merge)


def opt():
    parser = argparse.ArgumentParser(description="Any video convert to AVC / HEVC")
    parser.add_argument('-i', dest='video', help='input source', required=True)
    parser.add_argument('-t', dest='trim', help='trim start,end')
    parser.add_argument('-f', dest='fps', action='store_true', default=False, help='60 FPS')
    parser.add_argument('-m', dest='mode', type=int, help='Mode [1:x264 / 2:x265]', required=True)
    parser.add_argument('-d', dest='deint', action='store_true',
                        default=False, help='deinterlacing switch')
    parser.add_argument('-s', dest='res', type=str, default='1920x1080',
                        help='display resolution [default: 1920x1080]')
    parser.add_argument('-c', dest='config',
                        help='x26x params file', required=True)
    args = parser.parse_args()
    return args


def main():
    args = opt()
    source = args.video
    res = args.res
    mode = args.mode
    params = args.config
    trim = args.trim
    deint = args.deint
    fps = args.fps

    path = os.path.join(sys.path[0], "exec")
    avs = os.path.join(path, "avs4x26x.exe")
    if mode == 1:
        codec = os.path.join(path, "x264.exe")
        ext = ".264"
    elif mode == 2:
        codec = os.path.join(path, "x265.exe")
        ext = ".hevc"
    aac = os.path.join(path, "fdkaac.exe")
    ffmpeg = os.path.join(path, "ffmpeg.exe")
    mp4box = os.path.join(path, "mp4box", "mp4box.exe")

    t = ts2mp4(res, params, deint, fps, trim)
    avs_source = t.avsMethod(source)
    audio_source = t.audioMethod(ffmpeg, aac, source)
    video_source = t.videoMethod(avs, codec, avs_source, ext)
    t.mergeMethod(mp4box, video_source, audio_source)


if __name__ == "__main__":
    main()
