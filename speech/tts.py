import os, requests, time, json, logging
from xml.etree import ElementTree
import pydub
# pydub.AudioSegment.ffmpeg = "C:\\FFmpeg\\bin"
from pydub.playback import play
import io
from config import AZURE_TTS_FETCH_TOKEN_URL, AZURE_SPEECH_SERVICE_API_KEY, AZURE_TTS_VOICE


class TextToSpeech:
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None
        fetch_token_url = AZURE_TTS_FETCH_TOKEN_URL
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, text, wav):
        with open('data/audios/' + text + '-' + self.timestr + '.wav', 'wb') as audio:
            audio.write(wav)

    def synthesize(self, text, azurevoice=AZURE_TTS_VOICE, save=False):
        base_url = 'https://westus2.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'akspeech'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set('name', azurevoice) # use "en-US-Jessa24kRUS" for non-neural voice
        voice.text = str(text)
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
    
        if response.status_code == 200:
            logging.info("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
            play(pydub.AudioSegment.from_file(io.BytesIO(response.content), format="wav"))
            if save:
                self.save_audio(text, response.content)
        else:
            logging.error("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")


synthesizer = TextToSpeech(AZURE_SPEECH_SERVICE_API_KEY)

