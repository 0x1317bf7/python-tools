from urllib.parse import urlencode
from pyquery import PyQuery as py
from bs4 import BeautifulSoup
import requests
import time
import os
import re
import json

headers = {
    "Referer": "https://m.weibo.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

class FinishException(BaseException):
    pass


global uid
global prev_create_time

global root_path
global log
global config

def get_HTML_text(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except:
        return ""

def get_uid(name):
    try:
        url = "https://s.weibo.com/user?q=%s&Refer=SUer_box" % name
        html = get_HTML_text(url)

        plt = re.findall('class="s-btn-c" uid=([1-9][0-9]{9})', html)
        if len(plt) >= 1:
            return plt[0]
        return ""
    except:
        return ""

def print_log(content):
    log.write(content + "\n")
    print(content)

def get_scheme_json(js):
    js = str(js)
    s = js.index('"pics": ') + 8
    return js[s : js.index("]", s) + 1]

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def get_json_text(url):
    for i in range(10):
        response = requests.get(url = url, headers = headers)
        json_text = response.json()
        if json_text != None:
            return json_text
        print_log("在获取" + url + "时出现错误,将在10秒后重试")
        time.sleep(10)


def get_information(count):
    global prev_create_time
    global uid

    temp_create_time = prev_create_time

    params = {
        "uid": uid,
        "t": 0,
        "luicode": 10000011,
        "lfid": "100103",
        "type": int(uid),
        "value": int(uid),
        "containerid": '107603' + str(uid),
        "page": count
    }

    url = "https://m.weibo.cn/api/container/getIndex?" + urlencode(params)
    json_text = get_json_text(url)
    
    items = json_text.get("data").get("cards")

    changed = 0
    total = len(items)

    finished = 0

    for item in items:
        #print(item)
        if item.get("card_type") != 9:
            total -= 1
            continue
        mblog = item.get("mblog")
        
        created_at = mblog.get("created_at")
        
        print_log("正在获取" + created_at + "的微博")
        
        time_array = time.strptime(created_at,"%a %b %d %H:%M:%S %z %Y")

        create_time = int(time.mktime(time_array))

        temp_create_time = max(temp_create_time, create_time)

        if create_time <= prev_create_time:
            finished += 1
            if finished >= 2:
                raise FinishException()

        file_path = root_path + "/" + time.strftime("%Y年%m月%d日 %H时%M分%S秒", time_array)

        if mblog.get("pics") is None:
            try:
                url = mblog.get("page_info").get("urls").get("mp4_720p_mp4")
                response = requests.get(url = url, headers = {"User-Agent": "Lavf/57.83.100"})
                if not create_folder(file_path):
                    continue
                open(file_path + "/" + "video.mp4", "wb").write(response.content)
                changed += 1
            except Exception:
                total -= 1
            continue
            

        if not create_folder(file_path):
            continue

        pics = None
        try:
            scheme = item.get("scheme")
            html = requests.get(url = scheme, headers = headers).content.decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            js = soup.select("script")
            pics = json.loads(get_scheme_json(js))
        except Exception:
            pics = mblog.get("pics")

        for i in range(len(pics)):
            pic = pics[i]
            pic_url = pic.get("large").get("url")
            file_name = str(i + 1) + ".jpg"
            open(file_path + "/" + file_name, "wb").write(requests.get(pic_url).content)
        changed += 1

    if changed == 0 and total != 0:
        raise FinishException()
    return temp_create_time

def main(name, path = ""):
    
    global uid
    global prev_create_time

    global root_path
    global log
    global config
    
    root_path = path + name

    uid = int(get_uid(name))

    if not os.path.exists(root_path):
        os.makedirs(root_path)
    
    try:
        log = open(root_path + "/" + "logs.txt", "a")
    except Exception:
        pass

    print_log("将uid设置为" + str(uid) + "(" + name + ")")

    try:
        config = open(root_path + "/" + "config.txt", "r")
        prev_create_time = int(config.readline())
    except Exception:
        prev_create_time = 0
    
    temp_create_time = prev_create_time
    try:
        count = 1
        temp_create_time = get_information(count)
        temp_create_time = max(prev_create_time, temp_create_time)
        while True:
            count += 1
            get_information(count)
    except FinishException:
        print_log(str(uid) + "(" + name + ")的微博获取完毕,最新的微博更新时间为:" + str(temp_create_time))
        config = open(root_path + "/" + "config.txt", "w+")
        config.write(str(temp_create_time))

if __name__ == "__main__":
    name = input("请输入微博昵称:")
    main(name)
