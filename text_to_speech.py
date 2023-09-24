import os
from gtts import gTTS
from dotenv import load_dotenv
from google.cloud import texttospeech
from google.oauth2 import service_account

load_dotenv()

TTS_API_KEY = os.getenv('TTS_API_KEY')

if TTS_API_KEY is None:
    raise Exception('No API key found')

credentials = service_account.Credentials.from_service_account_file('tts_auth.json')

def generate_cantonese(cantonese, filename, google_tts=False):
    if google_tts is False:
        apikey = TTS_API_KEY
        voice = 'man-chi'
        url = f'https://api.narakeet.com/text-to-speech/m4a?voice={voice}'

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
            audio_encoding=texttospeech.AudioEncoding.MP3
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
    generate_cantonese('抌垃圾 唔該.','build/output3.mp4')
    # generate_english('Take out the trash, please.', 'english.mp4')