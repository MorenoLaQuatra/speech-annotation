# Another example chaining Bokeh's to Flask.
from flask import Flask, render_template, request, jsonify, make_response, redirect
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
    dataset = dataset.astype({"id": int}, errors='raise') 
    annotated_ids = []
    for path_file in glob.glob(AUDIO_BASE_PATH + "*.wav"):
        f_name = path_file.split("/")[-1]
        id_sentence = int(f_name.split(".")[0])
        annotated_ids.append(id_sentence)

    for i in annotated_ids:
        try:
            dataset.loc[(dataset.id == i), 'annotated'] = True
        except Exception as e:
            print (e)
    return dataset

DATASET = read_dataset("data/it-IT.jsonl")

def get_sentence():
    row = DATASET[DATASET["annotated"] == False].sample()
    sentence_text = row["utt"].item()
    sentence_id = int(row["id"].item())
    return sentence_text, sentence_id

@app.route("/")
def home():
    if request.cookies.get("allowed") == "yes":  
        sentence_text, sentence_id = get_sentence()
        ann_done = len(DATASET[DATASET["annotated"] == True])
        ann_all = len(DATASET)

        return render_template("index.html", 
                                sentence_text=sentence_text, 
                                sentence_id=sentence_id, 
                                ann_done=ann_done, 
                                ann_all=ann_all,
                                user_region=request.cookies.get("user_region"),
                                user_gender=request.cookies.get("user_gender"),
                                user_age_group=request.cookies.get("user_age_group"),
                                )
    else:
        return render_template("login.html")
    
@app.route("/set_user", methods=["POST"])
def login():
    fr = open("allowed_users.txt")
    usernames = fr.read()
    fr.close()
    usernames = usernames.split("\n")
    username = request.form.get("username")
    if username in usernames:
        res = make_response(redirect('/')) 
        res.set_cookie('allowed', "yes")
        return res
    else:
        return render_template("login.html")

def convert_webm_to_wav(file, filename):
    command = ['ffmpeg', '-y', '-i', file, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', AUDIO_BASE_PATH + filename + '.wav']
    subprocess.run(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)

@app.route("/send_recording", methods=["GET", "POST"])
def send_recording():
    rec = request.files.get("file")
    title = request.form.get("title")
    user_gender = request.form.get("user-gender")
    user_age_group = request.form.get("user-age_group")
    user_region = request.form.get("user-region")
    sentence_id = int(request.form.get("id"))
    filename = str(sentence_id)
    fw = open(f"{TEXT_BASE_PATH}{filename}.txt", "w", encoding="utf-8")
    fw.write(title)
    fw.close()
    rec.save(f"{WEBM_BASE_PATH}{filename}.webm")
    convert_webm_to_wav(f"{WEBM_BASE_PATH}{filename}.webm", filename=filename)
    DATASET.at[sentence_id, 'annotated'] = True
    data = {'message': 'Done', 'code': 'SUCCESS'}
    res = make_response(jsonify(data), 201)  
    res.set_cookie('user_gender', user_gender)
    res.set_cookie('user_age_group', user_age_group)
    res.set_cookie('user_region', user_region)
    return res

if __name__ == "__main__":
    app.run(debug=True, port=9876)
