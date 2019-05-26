import os
import urllib.parse

import requests
from bs4 import BeautifulSoup

from aip import AipSpeech
from pydub import AudioSegment
from tqdm import tqdm

from config import key_APP_ID
from config import key_API_KEY
from config import key_SECRET_KEY

def readdanci():
    with open(dancifilename, "r+", encoding="utf-8") as f:
        t = f.__next__()
        while t:
            yield t
            try:
                t = f.__next__()
            except StopIteration:
                t = ""


def synthesis(text, text1):
    # 语音合成
    APP_ID = key_APP_ID
    API_KEY = key_API_KEY
    SECRET_KEY = key_SECRET_KEY

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    result = client.synthesis(text, 'zh', 1, {
        'vol': 5, 'spd': 5, 'pit': 8, 'per': 0
    })
    if os.path.exists('temptype.mp3'):
        os.remove('temptype.mp3')
    # 单词类型
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('temptype.mp3', 'wb') as f:
            f.write(result)

    result = client.synthesis(text1, 'zh', 1, {
        'vol': 5, 'spd': 4, 'pit': 8, 'per': 0
    })
    if os.path.exists('tempdescribe.mp3'):
        os.remove('tempdescribe.mp3')

    # 单词解释声音
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('tempdescribe.mp3', 'wb') as f:
            f.write(result)


def outputmp3(urlstr, typestr, describestr):
    with requests.get(urlstr, headers=headers) as res:
        with open("tempmp3.mp3", "wb") as f:
            f.write(res.content)
    synthesis(typestr, describestr)
    if(os.path.exists('tempmp3.mp3')):
        songtype = AudioSegment.from_mp3("temptype.mp3")
        songdes = AudioSegment.from_mp3("tempdescribe.mp3")
        song  = AudioSegment.from_mp3("tempmp3.mp3")
        global total
        global slient
        total += song.append(slient) + songtype.append(slient) + songdes.append(slient)  + song.append(slient) + song.append(slient)
        os.remove('temptype.mp3')
        os.remove('tempdescribe.mp3')
        os.remove('tempmp3.mp3')


def parse_content(res):
    mp3url = ""
    typestr = ""
    describe = ""

    soup = BeautifulSoup(res.text, "lxml")
    header = soup.find("header", class_="word-details-pane-header")

    if(header is not None):
        mp3urlnode = header.find("span", class_="word-audio")
        mp3url = mp3urlnode["data-src"]

        simplenode = header.find("div", class_="simple")
        typestr = simplenode.find("h2").string

        for i in simplenode.find("ul").children:
            if(i.string != "\n"):
                describe = i.text
                break

    print("mp3 file名：{0}, 单词类型：{1}, 描述：{2}".format(mp3url, typestr, describe))
    outputmp3(mp3url, typestr, describe)


def parse_url(url):
    with requests.get(url, headers=headers) as res:
        parse_content(res)


dancifilename = "danci.txt"
rooturl = "https://dict.hjenglish.com/jp/jc/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "upgrade-insecure-requests": "1",
    "referer": "https://dict.hjenglish.com/",
    "cookie": "HJ_UID=b1b80aa2-7817-a147-201a-06ad22414eaa; \
                    HJ_SID=f5d5c06c-b8a5-9710-2c6a-e2ad58ebbcd7; \
                    "
}

# 最后的声音
total = AudioSegment.empty()
# 中间的空白声音
slient = AudioSegment.silent(duration=1000)

for url in tqdm(readdanci()):
    parse_url(rooturl + urllib.parse.quote(url))
    total.append(slient)

total.export('danci.mp3',format='mp3')
    # with open("test.html","w", encoding="utf-8") as file:
    #     file.write(res.text)
