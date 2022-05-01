# Another example chaining Bokeh's to Flask.
from flask import Flask, render_template, request, jsonify, make_response
import pandas as pd
import subprocess
import glob, os

app = Flask(__name__)

AUDIO_BASE_PATH = "annotations/audio/"
TEXT_BASE_PATH = "annotations/text/"
WEBM_BASE_PATH = "annotations/webm/"

def read_dataset(path):
    dataset = pd.read_json(path_or_buf=path, lines=True)
    dataset["annotated"] = False
    annotated_ids = []
    for path_file in glob.glob(AUDIO_BASE_PATH + "*.wav"):
        f_name = path_file.split("/")[-1]
        id_sentence = f_name.split(".")[0]
        annotated_ids.append(id_sentence)
    for i in annotated_ids:
        try:
            dataset.at[id_sentence, 'annotated'] = True
        except Exception as e:
            print (e)

    return dataset


DATASET = read_dataset("data/it-IT.jsonl")

def get_sentence():
    row = DATASET[DATASET.annotated == False].sample()
    sentence_text = row["utt"].item()
    sentence_id = row["id"].item()
    return sentence_text, sentence_id



@app.route("/")
def home():
    sentence_text, sentence_id = get_sentence()
    return render_template("index.html", sentence_text=sentence_text, sentence_id=sentence_id)

def convert_webm_to_wav(file, filename):
    command = ['ffmpeg', '-y', '-i', file, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', AUDIO_BASE_PATH + filename + '.wav']
    subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)

@app.route("/send_recording", methods=["GET", "POST"])
def send_recording():
    rec = request.files.get("file")
    title = request.form.get("title")
    sentence_id = int(request.form.get("id"))
    print (rec)
    print (title)
    print (sentence_id)
    filename = str(sentence_id)
    fw = open(f"{TEXT_BASE_PATH}{filename}.txt", "w", encoding="utf-8")
    fw.write(title)
    fw.close()
    rec.save(f"{WEBM_BASE_PATH}{filename}.webm")
    convert_webm_to_wav(f"{WEBM_BASE_PATH}{filename}.webm", filename=filename)
    data = {'message': 'Done', 'code': 'SUCCESS'}
    DATASET.at[sentence_id, 'annotated'] = True
    return make_response(jsonify(data), 201)

if __name__ == "__main__":
    app.run(debug=True, port=9876)
