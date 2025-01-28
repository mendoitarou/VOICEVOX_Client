import wave, sys, json, urllib.parse
from tkinter import *
import tkinter.ttk as ttk

import requests
import pyaudio
from tkinter import Listbox

CHUNK = 1024
VOICEVOX_API_URL = "http://localhost:50021"

# 初期の再生デバイスを指定
output_device_id = 24
#Voicemeeter AUX Input (VB-Audio

# 再生デバイスのリスト生成
setting_OutputDevice_List = ()
p = pyaudio.PyAudio()
i=0
while(i<p.get_device_count()):
    index = p.get_device_info_by_index(i)['index']
    #print(index)
    setting_OutputDevice_List = setting_OutputDevice_List + (f'{p.get_device_info_by_index(index)['name']}' ,)
    i+=1

# 再生テキストのログ
play_log = []

# ===== 関数定義 =====
def windows_show():
    generate_notification_window = Toplevel(root)
    generate_notification_window.title("生成中！ - VOICEVOX_CUSTOM_CLIENT")
    Generate_Notification_Text = ttk.Label(generate_notification_window, text='生成中です！お待ちください....')
    Generate_Notification_Text.pack()

def get_query(text, speaker_id):
    url = VOICEVOX_API_URL + f"/audio_query?text={urllib.parse.quote(text)}&speaker={speaker_id}"
    query_res = requests.post(url, headers={"accept": "application/json"})
    query_json = query_res.json()
    return query_json

def get_voice(query_json, speaker_id):
    url = VOICEVOX_API_URL + f"/synthesis?speaker={speaker_id}&enable_interrogative_upspeak=true"
    wav_res = requests.post(url, json=query_json, headers={"accept": "audio/wav", "Content-Type": "application/json"})
    path = "./output.wav"
    wr = open(path, "wb")
    wr.write(wav_res.content)
    wr.close()

def play_input_text():
    try:
        if(Input_Text.get() != ""):
            # 生成中を通知するウィンドウ(なぜか生成終わってからこれが実行されるんですね...なんで...???)
            #windows_show()

            # 生成開始
            # 変数にセット
            text = Input_Text.get()
            speaker_id = Speaker_ID.get()

            # ログに保存
            play_log.append(f'{speaker_id}: {text}')
            
            # クエリを取得
            query_json = get_query(text, speaker_id)
            
            # 音声生成
            get_voice(query_json, speaker_id)

            # 生成完了したのでウィンドウを削除
            #generate_notification_window.destroy()
            
            # 音声再生
            print("Play Audio")
            with wave.open("./output.wav", 'rb') as wf:
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True, output_device_index=output_device_id)
                while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
                    stream.write(data)
                stream.close()
                p.terminate()
        else:
            print("Nothing!")
    except Exception as e:
        print(f"[1]ERROR: {e}")
        exit()

def clear_text():
    Input_Text.set("")

def quit():
    global root
    root.destroy()
    exit()

def get_index_by_name(device_name):
    p = pyaudio.PyAudio()
    i=0
    flag_1=False
    while(flag_1==False):
        index = p.get_device_info_by_index(i)['index']
        if(p.get_device_info_by_index(index)['name'] == device_name):
            device_id = p.get_device_info_by_index(index)['index']
            flag_1=True
        i+=1
    return device_id

def setting_save():
    global output_device_id
    output_device_name = setting_OutputDevice_Combobox.get()
    print(output_device_name)
    output_device_id = get_index_by_name(output_device_name)
    
    setting_window.destroy()

def setting_show():
    global setting_OutputDevice_Combobox, setting_window
    # ウィンドウ生成
    setting_window = Toplevel(root)
    setting_window.title("設定 - VOICEVOX_CUSTOM_CLIENT")

    # オブジェクトの設定
    setting_title = ttk.Label(setting_window, text='設定')
    setting_OutPutDevice_Label = ttk.Label(setting_window, text='出力デバイスID')
    setting_OutputDevice = IntVar()
    setting_OutputDevice_Combobox = ttk.Combobox(setting_window, width=50 , values=setting_OutputDevice_List, textvariable=setting_OutputDevice)
    setting_save_button = ttk.Button(setting_window, text = '保存', command=lambda:setting_save())
    setiing_exit_button = ttk.Button(setting_window, text = '閉じる', command=lambda:setting_window.destroy())

    # レンダリング
    setting_title.grid(row=0, column=0)
    setting_OutPutDevice_Label.grid(row=2, column=0)
    setting_OutputDevice_Combobox.grid(row=2, column=1)
    setting_save_button.grid(row=3, column=0)
    setiing_exit_button.grid(row=3, column=1)

def log_show():
    print(play_log)
    log_window = Toplevel(root)
    log_window.title("ログ - VOICEVOX_CUSTOM_CLIENT")

    log_title = ttk.Label(log_window, text='ログ')
    log_list = Listbox(log_window, height=10, width=50)
    for i in play_log:
        log_list.insert(END, i)
    log_list.grid(row=1, column=0)
    log_title.grid(row=0, column=0)

# メインウィンドウ
# ウィンドウ生成
root = Tk()
root.title("VOICEVOX_CUSTOM_CLIENT")
root.resizable(False, False)
#root.attributes("-alpha", 0.75)

# オブジェクトの設定
Input_Text_Label = ttk.Label(root, text='テキスト:')
Input_Text = StringVar()
Input_Text_Entry = ttk.Entry(root, textvariable=Input_Text)

Speaker_ID_Label = ttk.Label(root, text='話者ID:')
Speaker_ID = IntVar()
Speaker_ID_Entry = ttk.Entry(root, textvariable=Speaker_ID)

play_button = ttk.Button(root,text = '再生', command=lambda:play_input_text())
clear_button = ttk.Button(root, text = 'クリア', command=lambda:clear_text())

setting_button = ttk.Button(root, text = '設定', command=lambda:setting_show())
log_button = ttk.Button(root, text = 'ログ', command=lambda:log_show())
exit_button = ttk.Button(root,text = '終了', command=lambda:quit())

# レンダリング
Input_Text_Label.grid(row=1,column=0)
Input_Text_Entry.grid(row=1,column=1)
Speaker_ID_Label.grid(row=2, column=0)
Speaker_ID_Entry.grid(row=2, column=1)

play_button.grid(row=3, column=0)
clear_button.grid(row=3, column=1)

setting_button.grid(row=4, column=0)
log_button.grid(row=4, column=1)
exit_button.grid(row=4, column=2)

# 初期設定を適応
Speaker_ID.set(2)

##ウィンドウの表示
root.mainloop()
