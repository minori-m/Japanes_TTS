"""Getting Started Example for Python 2.7+/3.3+"""
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import pandas as pd


# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="adminuser")
polly = session.client("polly")


csv_input = pd.read_csv("phrase2phrase_ver5_kai.csv")
for i in range(len(csv_input)):
    text = csv_input['linked_hiragana'][i]
    rhyme_pos = csv_input['rhyme_position_linked_yomi'][i].split("-")
    print(text)
    # print(rhyme_pos)
    
    ssml_text="<speak>"
    flag = 0
    #effextを書き換えるにはここを変える
    for j in range(len(text)):
        # print(j)
        # print("flag=",flag,"ssml=",ssml_text)
        if j!=int(rhyme_pos[0]) and flag==0:#1:強調部に入るまで,強調部出てから
            ssml_text = ssml_text + '<amazon:effect vocal-tract-length="-10%"><prosody volume="x-soft" >' + text[j]
            flag=1
        # print("loop1")
        elif j!=int(rhyme_pos[0]) and flag == 1:#2
            ssml_text=ssml_text+text[j]
        # print("loop2")
        elif j==int(rhyme_pos[0]) and flag==0:#3:最初から強調部
            ssml_text = ssml_text + '<amazon:effect vocal-tract-length="+18%"><prosody volume="x-loud" rate="80%" >' + text[j]
            flag = 2
        # print("loop3")
        elif j==int(rhyme_pos[0]) and flag==1:#4:強調部に入る
            ssml_text = ssml_text + '</prosody></amazon:effect><amazon:effect vocal-tract-length="+18%"><prosody volume="x-loud" rate="80%" >' + text[j]
            flag = 2
        # print("loop4")
        elif j!=int(rhyme_pos[1]) and flag == 2:#5:強調部の中
            ssml_text = ssml_text + text[j]
        # print("loop5")
        elif j==int(rhyme_pos[1]) and flag == 2:#6:強調部終わり
            ssml_text = ssml_text + text[j] + "</prosody></amazon:effect>"
            flag = 0
    # print("loop6")

if flag == 0:
    ssml_text =  ssml_text + "</speak>"
    elif flag ==1:
        ssml_text = ssml_text +"</prosody></amazon:effect></speak>"
# '''
# <speak>
# <amazon:effect name="whispered">こんにちは、</amazon:effect>
# <emphasis>ミズキ</emphasis>
# です。</speak>
# '''

mp3_name = str(i) + ".mp3"

try:
    # Request speech synthesis
    response = polly.synthesize_speech(OutputFormat="mp3",VoiceId="Takumi",TextType="ssml",Text=ssml_text)
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important as the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
    with closing(response["AudioStream"]) as stream:
        #output = os.path.join(gettempdir(), "speech.mp3")
        output = os.path.join(os.getcwd(), mp3_name)
        
        try:
            # Open a file for writing the output as a binary stream
            with open(output, "wb") as file:
                file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)

# # Play the audio using the platform's default player
# if sys.platform == "win32":
#     os.startfile(output)
# else:
#     # the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
#     opener = "open" if sys.platform == "darwin" else "xdg-open"
#     subprocess.call([opener, output])
