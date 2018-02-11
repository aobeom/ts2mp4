import os
import sys


class ffmpegConcat(object):
    def __init__(self, program, formats):
        self.program = program
        self.formats = formats

    def __dotCheck(self):
        formats = self.formats
        if formats:
            if formats.startswith("."):
                formats = formats
            else:
                formats = "." + formats
        else:
            formats = ".mp4"
        return formats

    def __getVideo(self, formats):
        videos = []
        filelist = os.listdir(".")
        for f in filelist:
            filename = os.path.splitext(f)[0]
            extension = os.path.splitext(f)[1]
            if filename.isdigit() and extension != ".py":
                if extension == formats:
                    newname = filename.zfill(4) + extension
                    os.rename(filename + extension, newname)
                    videos.append(newname)
        return sorted(videos)

    def videoMP4toTS(self):
        oriVideo = self.__getVideo(self.formats)
        length = len(oriVideo)
        if length != 0:
            for newVideo in oriVideo:
                filename = os.path.splitext(newVideo)[0]
                command = '{} -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts -y {}.ts'.format(
                    self.program, newVideo, filename)
                os.system(command)
        else:
            errorMsg = "No {}".format(self.formats)
            raw_input(errorMsg)
            sys.exit()

    def videoTSconcat(self):
        tsVideos = self.__getVideo(".ts")
        length = len(tsVideos)
        name = "all"
        segement = "|"
        if length != 0:
            oriVideos = segement.join(tsVideos)
            command = '{} -i "concat:{}" -c copy -bsf:a aac_adtstoasc -movflags +faststart -y "{}.mp4"'.format(
                self.program, oriVideos, name)
            os.system(command)
            for ts in tsVideos:
                os.remove(ts)


def main():
    ffmpeg = os.path.join(sys.path[0], "exec", "ffmpeg.exe")
    formats = raw_input("Format(.mp4)")
    concat = ffmpegConcat(ffmpeg, formats)
    concat.videoMP4toTS()
    concat.videoTSconcat()


if __name__ == "__main__":
    main()
