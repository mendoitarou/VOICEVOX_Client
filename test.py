import wave, sys, json, urllib.parse

import requests
import pyaudio

CHUNK = 1024
output_device_id = 24

VOICEVOX_API_URL = "http://localhost:50021"

print("========= VOICEVOX_API_TESTER =========")

text = "テストボイスだよ"
speaker_id = 2

print(f"TEXT: {text}")
print(f"SPEAKER_ID: {speaker_id}")

try:
    url = VOICEVOX_API_URL + f"/audio_query?text={urllib.parse.quote(text)}&speaker={speaker_id}"
    query_res = requests.post(url, headers={"accept": "application/json"})
    query_json = query_res.json()
    #print("QUERY_JSON: ")
    #print(json.dumps(query_res.json(), indent=4))
except Exception as e:
    print(f"[1]ERROR: {e}")
    exit()

try:
    url = VOICEVOX_API_URL + f"/synthesis?speaker={speaker_id}&enable_interrogative_upspeak=true"
    wav_res = requests.post(url, json=query_json, headers={"accept": "audio/wav", "Content-Type": "application/json"})
    path = "./output.wav"
    wr = open(path, "wb")
    wr.write(wav_res.content)
    wr.close()
except Exception as e:
    print(f"[2]ERROR: {e}")
    exit()

try:
    with wave.open("./output.wav", 'rb') as wf:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True, output_device_index=output_device_id)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            stream.write(data)
        stream.close()
        p.terminate()
except Exception as e:
    print(f"[3]ERROR: {e}")
    exit()


#try:
#    p = pyaudio.PyAudio()
#    i=0
#    while(i<p.get_device_count()):
#        print(p.get_device_info_by_index(i))
#        i+=1
#except Exception as e:
#    print(f"[4]ERROR: {e}")
#    exit()
