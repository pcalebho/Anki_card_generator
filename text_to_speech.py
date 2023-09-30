import os
import re
from gtts import gTTS
from dotenv import load_dotenv
from google.cloud import texttospeech
from google.oauth2 import service_account

load_dotenv()

TTS_API_KEY = os.getenv('TTS_API_KEY')

if TTS_API_KEY is None:
    raise Exception('No API key found')

credentials = service_account.Credentials.from_service_account_file('tts_auth.json')

def generate_cantonese(cantonese, filename, voice_speed=1.0, google_tts=True):
    cantonese = re.sub(r'\?','', cantonese)
    if google_tts is False:
        apikey = TTS_API_KEY
        voice = 'man-chi'
        url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}&voice-speed={voice_speed}'

        import requests

        options = {
            'headers': {
                'Accept': 'application/octet-stream',
                'Content-Type': 'text/plain',
                'x-api-key': apikey,
            },
            'data': cantonese.encode('utf8')
        }

        with open(filename, 'wb') as f:
            f.write(requests.post(url, **options).content)

    else:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=cantonese)

        voice = texttospeech.VoiceSelectionParams(
            language_code="yue-HK", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_speed
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)



def generate_english(english, filename):
    tts = gTTS(english, lang='en', tld='us')
    tts.save(filename)

if __name__ == '__main__':
    yue = '今日几号?'
    en = 'I will find something.'

    generate_cantonese(yue,'build/ch_normal.mp3', voice_speed=1, google_tts=True)
    generate_cantonese(yue,'build/ch_slow.mp3', voice_speed=0.5, google_tts=True)
    generate_english('I will find something.', 'build/en.mp3')
