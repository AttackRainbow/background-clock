import json
import os
import sys
from time import sleep, time

LIMIT = 2
for i in range(5):
    try:
        from keyboard import is_pressed
        from pydub import AudioSegment
        from pydub.playback import play
        from pytube import YouTube
        from pytube.exceptions import RegexMatchError
    except ImportError:
        if i == LIMIT:
            print("Cannot install dependency...")
            exit(1)
        os.system(sys.executable + " -m pip install -r requirements.txt")
    else:
        break

CONFIG_FILE = "config.json"


def main():
    os.system("cls")  # to clear warnings

    file_name = sys.argv[0].split("/")[-1].replace(".py", "")
    try:
        minutes = int(file_name)
    except TypeError:
        print("The file name, " + file_name +
              ", is inconvertible to type int.")
        exit(1)

    if not os.path.exists(CONFIG_FILE):
        default = {"audio_file": None, "adjust_dB": 0,
                   "play_dur_sec": None, "ffmpeg_path": None}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f)
        setup_audio(default)

    config = read_config()
    audio_file = config["audio_file"]
    if not audio_file:
        setup_audio(config)
        config = read_config()
    AudioSegment.converter = config["ffmpeg_path"]
    audio = AudioSegment.from_file(audio_file)
    audio += float(config["adjust_dB"])
    if config["play_dur_sec"]:
        audio = audio[:int(config["play_dur_sec"])]

    main_loop(minutes, audio)


def read_config():
    with open(CONFIG_FILE, encoding="utf8") as f:
        config = json.loads(f.read())
    return config


def setup_audio(config):

    while True:
        link = input("Link to YouTube video: ")
        try:
            streams = YouTube(link).streams
        except RegexMatchError:
            print("Invalid YouTube link")
        else:
            break

    ffmpeg_path = input("path to ffmpeg.exe: ")
    AudioSegment.converter = ffmpeg_path
    file = streams.filter(only_audio=True)[0].download()
    audio = AudioSegment.from_file(file)

    adjust_dB = 0
    while True:
        # play sound to see if volume needs to be turned down
        play(audio[:2000])
        adjust = input("Adjust dB of volume? (y,n): ")
        if adjust == "y":
            db_str = input("How much? (can be negative to lower the volume): ")
            try:
                adjust_dB = float(db_str)
            except ValueError:
                print(
                    f"{db_str} cannot be converted to floating point number.")
            else:
                audio += adjust_dB
        else:
            break

    while True:
        how_long_s = input(
            "How long to play is sec? (number or blank to play the whole duration): ")
        if not how_long_s:
            how_long_s = None
            break
        try:
            how_long_ms = int(how_long_s * 1000)
        except ValueError:
            print(
                f"{how_long_s} cannnot be converted to a floating point number.")
        else:
            break

    # save config
    config["audio_file"] = file
    config["adjust_dB"] = adjust_dB
    config["play_dur_sec"] = how_long_s
    config["ffmpeg_path"] = ffmpeg_path
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

    print("You can modify the audio in " + CONFIG_FILE + '.')


def main_loop(minutes,  audio):

    play(audio)
    start = time()
    while True:
        elapsed = time() - start
        if elapsed >= minutes * 60:
            play(audio)
            start = time()

        if is_pressed("ctrl + space"):
            exit(0)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system('title "Background Clock"')
    main()
