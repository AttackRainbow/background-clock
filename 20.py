import os
import sys
from time import time
from typing import Type
from winsound import Beep

LIMIT = 2
for i in range(5):
    try:
        from keyboard import is_pressed
        from pydub import AudioSegment
        from pydub.playback import play
    except ImportError:
        if i == LIMIT:
            print("Cannot install dependency...")
            exit(1)
        os.system(sys.executable + " pip install -r requirements.txt")
    else:
        break


def main():
    try:
        minutes = int(sys.argv[0].split("/")[-1].replace(".py", ""))
    except TypeError:
        print("The file name is inconvertible to type int.")
        exit(1)

    file_name_without_ext = "sound"
    files = [e for e in os.listdir() if file_name_without_ext in e]

    audio = None
    if files:
        file = files[0]
        audio = AudioSegment.from_file(file)

        adjust_dB_file = "dB.text"
        if not os.path.exists(adjust_dB_file):
            with open(adjust_dB_file, "w") as f:
                f.write("0")
        dB = 0
        with open(adjust_dB_file) as f:
            try:
                dB = float(f.read().replace('\n', ''))
            except ValueError:
                print(
                    f"dB in {adjust_dB_file} cannot be converted to floating point number.")
        audio += dB

    main_loop(minutes, audio)


def main_loop(minutes,  audio=None):
    freq = 380
    play_dur_milisec = 2000

    audio_to_play = None
    if audio:  # to let user know that it has started
        fade_out_milisec = 500
        audio_to_play = audio[:play_dur_milisec].fade_out(fade_out_milisec)
        play(audio_to_play)

    start = time()
    while True:
        elapsed = time() - start
        if elapsed >= minutes * 60:
            if audio_to_play:
                play(audio_to_play)
            else:
                Beep(freq, play_dur_milisec)
            start = time()

        if is_pressed("ctrl + space"):
            exit(0)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system('title "Background Clock"')
    main()
