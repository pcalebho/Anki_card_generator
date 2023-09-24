import os
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

TTS_API_KEY = os.getenv('TTS_API_KEY')

if TTS_API_KEY is None:
    raise Exception('No API key found')

def generate_cantonese(cantonese):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient(credentials=TTS_API_KEY)       #type: ignore

    input_text = texttospeech.SynthesisInput(text=cantonese)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="yue-HK",
        name="yue-HK-Standard-C",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')



def generate_english(english, filename):
    tts = gTTS(english, lang='en', tld='us')
    tts.save('build/' + filename)

if __name__ == '__main__':
    generate_cantonese('抌垃圾 唔該.')
    # generate_english('Take out the trash, please.', 'english.mp4')