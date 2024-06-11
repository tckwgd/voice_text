# -*- coding: utf-8 -*-
import os
import time
import wave
import json
import subprocess
from pydub import AudioSegment, silence
import speech_recognition as sr

def install_dependencies():
    # Install necessary libraries
    subprocess.run(["pip", "install", "pydub", "speechrecognition"])
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"])

def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    # Convert MP3 file to WAV file using pydub
    try:
        print("开始将 MP3 文件转换为 WAV 文件...")
        audio = AudioSegment.from_mp3(mp3_file_path)
        audio.export(wav_file_path, format="wav")
        print("转换完成。")

        if os.path.exists(wav_file_path):
            print("WAV 文件成功生成。")
        else:
            print("WAV 文件生成失败。")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")

def recognize_speech(wav_file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_file_path) as source:
            print("开始语音识别...")
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='zh-CN')
            print("语音识别完成。")
            print("识别的文本:")
            print(text)
    except Exception as e:
        print(f"语音识别过程中出现错误: {e}")

def split_audio(file_path, chunk_length_ms=60000):
    audio = AudioSegment.from_wav(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunks.append(audio[i:i + chunk_length_ms])
    return chunks

def recognize_speech_from_chunks(chunks, retries=3):
    recognizer = sr.Recognizer()
    results = []
    for i, chunk in enumerate(chunks):
        chunk.export(f"/content/chunk_{i}.wav", format="wav")
        for attempt in range(retries):
            try:
                with sr.AudioFile(f"/content/chunk_{i}.wav") as source:
                    print(f"开始识别第 {i+1} 个片段...")
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language='zh-CN')
                    print(f"第 {i+1} 个片段识别完成。")
                    results.append(text)
                    break
            except sr.RequestError as e:
                print(f"请求错误: {e}")
                if attempt < retries - 1:
                    print(f"重试中 ({attempt + 1}/{retries})...")
                    time.sleep(5)  # 等待5秒后重试
            except sr.UnknownValueError:
                print("Google 语音识别引擎无法理解音频")
                results.append("[Unrecognized]")
                break
            except Exception as e:
                print(f"语音识别过程中出现错误: {e}")
                if attempt < retries - 1:
                    print(f"重试中 ({attempt + 1}/{retries})...")
                    time.sleep(5)  # 等待5秒后重试
    return results

def main():
    install_dependencies()
    
    # Define file paths
    mp3_file_path = "/20240611 書 2 - 金牧.mp3"
    wav_file_path = "/content/audio.wav"

    # Convert MP3 to WAV
    convert_mp3_to_wav(mp3_file_path, wav_file_path)

    # Recognize speech from entire file
    recognize_speech(wav_file_path)

    # Split audio into chunks and recognize speech from each chunk
    chunks = split_audio(wav_file_path)
    print(f"音频文件分割成 {len(chunks)} 个片段。")
    recognized_texts = recognize_speech_from_chunks(chunks)

    # Combine recognized text
    final_text = " ".join(recognized_texts)
    print("识别的完整文本:")
    print(final_text)

if __name__ == "__main__":
    main()
