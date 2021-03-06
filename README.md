# speech-annotation
Basic and simple web app for text-to-speech audio annotations.

Given the input text annotate it with following data:
- audio recording (in `annotations/audio/ID_FILE.wav`)
- speaker metadata (in `annotations/json/ID_FILE.json`)

**Requirements** are listed on `requirements.txt`but you also need a system with `ffmpeg` installed for `webm`to `wav` conversion.

**CAVEAT:** the project is created for a basic and specific use-case (even metadata annotations are just referred to the use-case).

# Usage
1. `git clone https://github.com/MorenoLaQuatra/speech-annotation.git`
2. `cd speech-annotation`
3. `pip install -r requirements.txt`
4. Install [ffmpeg](https://ffmpeg.org/download.html)
5. Create a file `allowed_users.txt` containing usernames of users that can annotate data (no passwords). Each username in a separate line.
6. `python app.py`
7. Go to `localhost:9876` in your browser
8. Find annotations in `speech-annotation/annotations/audio/`

If you want to run it over internet execute it with the following command: `flask run --host=0.0.0.0 --port=9876 --cert=adhoc`, SSL connection is required to access user microphone.



# Todo:
- [x] Login Wall - `allowed_users.txt` contains the list of usernames (no password)
- [x] Collection of metadata - in `annotations/json/ID_FILE.json`
- [ ] Support for other datasets (?) - currently italian split of MASSIVE
