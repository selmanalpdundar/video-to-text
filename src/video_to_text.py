from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import speech_recognition as sr
import subprocess


class VideoToText(object):
    def __init__(self, language="en-US") -> None:
        # Create a speech recognition object
        self.langue = language
        self.r = sr.Recognizer()

    def convert(self, path):
        print("Progress - Converting video to sound started.")
        self.convert_video_to_audio(path)
        print("Progress - Converting video to sound finished.")

        print("Progress - Converting sound to text started")

        result = self.transcribe_large_audio(f"{path.split('.')[0]}.wav")

        print(result, file=open(path.split(".")[0].split("/")[-1] + ".txt", "w"))
        print("Progress - Converting sound to text Finished")

    def convert_video_to_audio(self, path="1.mp4"):
        command = (
            f"ffmpeg -i {path} -ab 160k -ac 2 -ar 44100 -vn {path.split('.')[0]}.wav"
        )
        subprocess.call(command, shell=True)

    def transcribe_large_audio(self, path):
        """Split audio into chunks and apply speech recognition"""
        # Open audio file with pydub
        sound = AudioSegment.from_wav(path)

        # Split audio where silence is 700ms or greater and get chunks
        chunks = split_on_silence(
            sound, min_silence_len=700, silence_thresh=sound.dBFS - 14, keep_silence=700
        )

        # Create folder to store audio chunks
        folder_name = "audio-chunks_" + path.split(".")[0].split("/")[-1]
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)

        whole_text = ""
        # Process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # Export chunk and save in folder
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")

            # Recognize chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = self.r.record(source)
                # Convert to text
                try:
                    text = self.r.recognize_google(audio_listened, language=self.langue)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text

        # Return text for all chunks
        return whole_text


if __name__ == "__main__":
    print("Enter the audio file path")

    path = input()
    converter = VideoToText()
    converter.convert(path=path)
