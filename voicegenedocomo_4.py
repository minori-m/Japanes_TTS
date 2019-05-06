# -*- coding:utf-8 -*-

"""
 Mac上で指定したテキストから、docomoの音声合成APIのバイナリデータをwavデータに保存する
"""

import os
import sys
import datetime
import argparse
import subprocess
import requests
import pprint
import json

# config
# ===========================================

#バイナリデータの一時保存場所
tmp = "./cache/"

# wavデータの保存場所
soundDir = "./sound/"

#Docomo 音声合成 API
API_KEY = '*************************'
url = "https://api.apigw.smt.docomo.ne.jp/crayon/v1/textToSpeechKanaAccent?APIKEY="+API_KEY


# aitalk パラメーター設定
# ===========================================

"""
参考）音声合成 | docomo Developer support
https://dev.smt.docomo.ne.jp/?p=docs.api.page&api_name=text_to_speech&p_name=api_1#tag01

    'speaker' : "nozomi"、"seiji"、"akari"、"anzu"、"hiroshi"、"kaho"、"koutarou"、"maki"、"nanako"、"osamu"、"sumire"
    'pitch' : ベースライン・ピッチ。 基準値:1.0、範囲:0.50～2.00
    'range' : ピッチ・レンジ。基準値:1.0、範囲:0.00～2.00
    'rate' : 読み上げる速度。基準値:1.0、範囲:0.50～4.00
    'volume' : 音量。基準値:1.0、範囲:0.00～2.00
"""

# prm = {
#     'speaker' : 'nozomi',
#     'pitch' : '1',
#     'range' : '1',
#     'rate' : '1',
#     'volume' : '1.5'
# }

# パラメーター受取
# ===========================================
#%% arguments
# #parser = argparse.ArgumentParser()
# parser.add_argument('--text',      type=str,   required=True)
# args = parser.parse_args()
# text = args.text


# SSML生成
# ===========================================
# xml = u'<?xml version="1.0" encoding="utf-8" ?>'
# voice = '<voice name="' + prm["speaker"] + '">'
# prosody = '<prosody rate="'+ prm['rate'] +'" pitch="'+ prm['pitch'] +'" range="'+ prm['range'] +'">'
# xml += '<speak version="1.1">'+ voice + prosody + text + '</prosody></voice></speak>'

# # utf-8にエンコード
# xml = xml.encode("UTF-8")

#カナアクセント文
kana = {
  "Command":"AP_Synth",
  "SpeakerID":"1",
  "StyleID":"1",
  "SpeechRate":"1.15",
  "AudioFileFormat":"0",
  "TextData":"エヌティーティーノ[/05]オンセーゴーセーエンジンニ[*09]ヨル[/00]オンセーデス^[.01]"
}



# Docomo APIアクセス
# ===========================================
print("Start API")

response = requests.post(
    url,
    data=json.dumps(kana)
)

#print(response)
#print(response.encoding)
#print(response.status_code)
#print(response.content)

if response.status_code != 200 :
    print("Error API : " + response.status_code)
    exit()

else :
    print("Success API")

#現在日時を取得
now = datetime.datetime.now()
tstr = datetime.datetime.strftime(now, '%Y%m%d-%H%M%S')

#保存するファイル名
rawFile = tstr + ".raw"
wavFile = tstr + ".wav"

#バイナリデータを保存
fp = open(tmp + rawFile, 'wb')
fp.write(response.content)
fp.close()

print("Save Binary Data : " + tmp + rawFile)


# バイナリデータ → wav に変換
# ===========================================

# macのsoxを使って raw→wavに変換
cmd = "sox -t raw -r 16k -e signed -b 16 -B -c 1 " + tmp + rawFile + " "+ soundDir + wavFile
# コマンドの実行
subprocess.check_output(cmd, shell=True)

print("Done : " +soundDir + wavFile)
