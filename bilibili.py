#encoding=utf-8

from genericpath import exists

import os
import shutil
import json

ffmpeg_path = None

class Listener:
    def onFile(file):
        pass

def dfs(root, listener):
    print("进入" + root)
    for file in os.listdir(root):
        path = os.path.join(root, file)
        if os.path.isfile(path):
            listener.onFile(path)
        elif os.path.isdir(path):
            dfs(path, listener)

def to_filename(filename):
    return filename.replace("\\", " ").replace("/", " ").replace(":", " ").replace("*", " ").replace("?", " ").replace("\"", " ").replace("<", " ").replace(">", " ").replace("|", " ")

def cmd(command):
    print("执行 " + command)
    return os.system(command)

def delete(file):
    print("删除" + file)
    if os.path.isdir(file):
        shutil.rmtree(file)
    else:
        os.remove(file)
    

def rename(old, new):
    print("将" + old + "重命名为" + new)
    os.rename(old, new)

def video_to_audio(video, output = None, delete_origin = False):
    if output == None:
        output = remove_suffix(video) + ".mp3"
    command = "ffmpeg -i \"" + video + "\" -vn \"" + output + "\""
    if ffmpeg_path != None:
        command = ffmpeg_path + " " + command
    cmd(command)
    if delete_origin:
        delete(video)

def video_to_video(video, output = None, delete_origin = False):
    if output == None:
        output = remove_suffix(video) + "_new" + get_suffix(video)
    command = "ffmpeg -i \"" + video + "\" -an \"" + output + "\""
    if ffmpeg_path != None:
        command = ffmpeg_path + " " + command
    cmd(command)
    if delete_origin:
        delete(video)



'''
video，audio，output都是绝对路径
'''
def merge_video_and_audio(video, audio, output = None, delete_origin = False):
    if output == None:
        output = remove_suffix(video) + ".mp4"
    command = "ffmpeg -i \"" + video + "\" -i \"" + audio + "\" -c:v copy -c:a aac -strict experimental \"" + output + "\""
    if ffmpeg_path != None:
        command = ffmpeg_path + " " + command
    cmd(command)
    if delete_origin:
        delete(video)
        delete(audio)

def check_ffmpeg():
    command = "ffmpeg -version"
    if ffmpeg_path != None:
        command = ffmpeg_path + " " + command
    result = cmd(command)
    return result == 0

def remove_suffix(text):
    index = text.rindex(".")
    if index >= 0 and index < len(text):
        return text[0:index]
    return text

def get_suffix(text):
    index = text.rindex(".")
    if index >= 0 and index < len(text):
        return text[index + 1:len(text)]
    return text


def format_audio(root):
    files = os.listdir(root)
    if len(files) <= 0:
        return
    files.sort()
    name = None
    for file in files:
        if not os.path.isdir(root + os.sep + file):
            continue
        info_path = root + os.sep + file + os.sep + "entry.json"
        if not os.path.exists(info_path):
            continue

        dir_name = None
        strid = None
        subtitle = None
        with open(info_path, "r", encoding="utf-8") as info:
            data = json.load(info)
            if name == None:
                name = to_filename(data["title"])
            dir_name = to_filename(data["type_tag"])
            if len(files) > 1:
                try:
                    strid = to_filename(str(data["ep"]["index"]))
                    subtitle = to_filename(str(data["ep"]["index_title"]))
                except BaseException:
                    strid = to_filename(str(data["page_data"]["page"]))
                    subtitle = to_filename(str(data["page_data"]["part"]))
        file_name = root + os.sep + (name if strid == None else strid + " " + subtitle)
        print(file_name)
        if dir_name.find("flv") != -1:
            #旧版    
            file_name = file_name + ".flv"
            rename(root + os.sep + file + os.sep + dir_name + os.sep + "0.blv", file_name)
        else:
            #新版
            file_name = file_name + ".mp4"
            audio = root + os.sep + file + os.sep + dir_name + os.sep + "audio.m4s"
            video = root + os.sep + file + os.sep + dir_name + os.sep + "video.m4s" 
            merge_video_and_audio(video, audio, file_name, False)  
        delete(root + os.sep + file)
    return name

def format(root_path):
    files = os.listdir(root_path)
    for file in files:
        path = os.path.join(root_path, file)
        if (os.path.isdir(path)):
            name = format_audio(path)
            if name != None:
                rename(path, os.path.join(root_path, name))

def to_audio(root_path):
    class MyListener(Listener):
            def onFile(self, file):
                if file.endswith(".flv") or file.endswith(".mp4"):
                    video_to_audio(file, remove_suffix(file) + ".mp3")
    listener = MyListener()

    dfs(root_path, listener)


def main():
    print("检查ffmpeg版本:")
    if not check_ffmpeg():
        global ffmpeg_path
        ffmpeg_path = input("未检测到ffmpeg，请输入ffmpeg路径")
        if not check_ffmpeg():
            print("未检测到ffmpeg，请将ffmpeg.exe放入命令行所在文件夹或加入path中")
            cmd = input("是否继续？你的数据可能被删除\n(1)yes\n(2)no\n")
            if cmd != "1":
                return

    root_path = input("请输入根目录\n")
    command = input("1.整理下载视频\n2.视频转音频\n0.退出\n")
    if command == "1":
        format(root_path)
    elif command == "2":
        to_audio(root_path)
    else:
        return

if __name__ == "__main__":
    main()
