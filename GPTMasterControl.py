import openai  #ChatGPT
import elevenlabs  #Voice API
import pvporcupine as pv  #Wake Word Detection
from elevenlabs import generate, stream, play, Voice, VoiceSettings, voices #ElevenLabs voice generation
import speech_recognition as sr  #Google Speech Recognition

from elevenlabs.client import ElevenLabs

import pyaudio
from pydub.playback import play as pydubPlay
import numpy as np
import os
import json

import MasterRobotFunctions as robot

# change CWD to current dir:
os.chdir('C:/<path-to-directory>/AIRobotCarControl-Public') # << change this directory to your install directory

# Set OpenAI API key
openai.api_key = '<openAI-key-here>' # << paste your OpenAI API Key here

# Set ElevenLabs Client and API Key
xi_api_key = "<xi-api-key>" # << paste your ElevenLabs API Key here
client = ElevenLabs(api_key=xi_api_key)
voices = voices()

# Set PicoVoice AI Access Key
pv_access_key='<pv-access-key-here>' # << paste your PVPorcupine Access Key here

#PV Keyword Path:
keyword_path = 'assets/JARVISWakeWordNeov1.ppn' # << If changing your keyword, change the path to reflect that

chat_history = [
    {
        "role": "system",
        "content": "You are a highly sophisticated assistant, whose job is to control a tank-drive wheeled robot using python functions described to you.  Your replies will ALWAYS be of the format <function();> <text_reply>, as this is how you will control the robot."
    },
    {
        "role": "user",
        "content": """Your functions are:  
driveDistance(int distance, int speed) - a function that moves the robot a certain distance in centimeters.  The function will not return anything.  The speed for all drive motors is in the range of 0 to 255.
turn(int angle, int speed) - a function that turns the robot by a certain number of degrees.  The function will not return anything.
getUlsReading(int angle, int numReadings) - a function that will turn the ultrasonic rangefinder by a number of degrees relative to the front of the robot, then take the specified amount of range readings and average them to provide a distance between the sensor and an object.  This function returns the averaged distance in centimeters.
ghostFunction(int a1, int a2) - this is a function that you can use if you don't want to do anything with the robot.  This allows you to respond to me conversationally only instead of taking an action.  Only use this function if I am not asking you to do anything with the robot.
Can you confirm your understanding of these functions by sending a command to the robot?
"""
    },
    {
        "role": "assistant",
        "content": "driveDistance(10, 255);  OK, moving robot now."
    },
    {
        "role": "user",
        "content": "turn left 90 degrees"
    },
    {
        "role": "assistant",
        "content": "turn(-90, 100);  I'm turning the robot now."
    }
]

def callFunctionStep2(input):
    func_parts = input.split('(')
    func_name = func_parts[0]
    func_params = func_parts[1].split(')')
    func_params_diff = func_params[0].split(',')
    param1 = int(func_params_diff[0])
    param2 = int(func_params_diff[1])
    callFunction(func_name, param1, param2)

def callFunction(function_name, param1, param2):
    rfunc = getattr(robot, function_name)
    return rfunc(param1, param2)

class JARVIS:
    def __init__(self, autoMode, snarkiness=0, helpfulness=1, tone_length=2000):
        self.snarkiness = snarkiness
        self.helpfulness = helpfulness
        self.tone_length = tone_length
        if autoMode == True:
            self.pv = pv.create(access_key=pv_access_key, keyword_paths=[keyword_path], sensitivities=[0.3])
            self.r = sr.Recognizer()
            
    def listen_for_wake_word(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=self.pv.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.pv.frame_length)
        while True:
            pcm = np.frombuffer(stream.read(self.pv.frame_length), dtype=np.int16)
            if self.pv.process(pcm) == 0:
                return True

    def transcribe_audio(self):
        try:
            with sr.Microphone() as source:
                print("Listening for command...")
                audio = self.r.listen(source)
                text = self.r.recognize_google(audio)

                print("Text: " + text)
            return text
        
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
            return None
        except sr.RequestError:
            print("API unavailable. Please check your internet connection.")
            return None

    def get_gpt4_reply(self, text):
        chat_history.append(
        {
            "role": "user",
            "content": text,
        }
    )

        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo", 
          messages=chat_history,
          temperature=0,
          max_tokens=self.tone_length
        )

        chat_history.append(
            {
                "role": "assistant",
                "content" : response.choices[0]['message']['content'].strip(),
            }
        )
        responseMSG = chat_history[-1]["content"].strip()

        print("Reply from GPT: " + responseMSG + "\n")

        responseList = responseMSG.split(';')
        if len(responseList) > 1:
            functionToCall = responseList[0].strip()
            returnMessage = responseList[1].strip()
        
        if functionToCall:
            robotFeedback = callFunctionStep2(functionToCall)
            if robotFeedback:
                chat_history.append(
                    {
                        "role": "user",
                        "content": robotFeedback,
                    }
                )
        
        return returnMessage

    def new_tts_all_in_one(self, text):

        # Voices:
        jarvis = "CJroK8SRteDKFPQ1rZeQ" # << may need to replace if it doesn't work - you could pick any voice

        audio = generate(
            api_key=xi_api_key,
            text=text,
            voice=Voice(
                voice_id=jarvis,
                settings=VoiceSettings(stability=1, similarity_boost=0.1, style=0.1, use_speaker_boost=True)
            ),
            model="eleven_monolingual_v1"
        )

        play(audio)

    def manualTest(self):
        print("Manual Test Initiated:\n")
        message = input()
        responseMSG = message.strip().split(';')

        if len(responseMSG) > 1:
            functionToCall = responseMSG[0].strip()
            returnMessage = responseMSG[1].strip()

            print(responseMSG[0])
            print(responseMSG[1])

        callFunctionStep2(functionToCall)
        print(returnMessage + "\n")
            


    def start(self):
        auto = True # << change to false for Manual Test
        if(auto == True):
            print("Auto Mode: \n\n")
            shutdown = False
            while(shutdown != True):
                print("\n")
                if self.listen_for_wake_word():
                    print("Wake word detected.")
                    text = self.transcribe_audio()
                    if text is None:
                        print("I'm sorry, I didn't hear you correctly. Exiting.")
                        return
                    if text == "turn off":
                        shutdown = True
                    reply = self.get_gpt4_reply(text)
                    self.new_tts_all_in_one(reply)
        else:
            while(True):
                self.manualTest()

# Startup:
print(keyword_path + "\n")
print(os.getcwd() + "\n")
print("GPT INITIALIZING...\n")
jarvis = JARVIS(autoMode=True, snarkiness=0.5, helpfulness=0.5, tone_length=200) # << change 'autoMode' to false for Manual Test
print("JRC STARTING\n")
jarvis.start()