from gtts import gTTS
from google.cloud import texttospeech
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('google_auth.json')

def gen_target_audio(target_lang_text, filename, lang_code, voice_speed=1.0):
    """
    Generate Cantonese sound clip from text.

    Args:
        target_lang_text (str): text of your target language
        lang_code (str): TTS language code from Google Cloud. Decides what language the synthesizer will speak.
        filename (str): filepath where audio file is generated
        voice_speed(float): Speed of audio file
    """

    # Instantiates a client
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=target_lang_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
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
    """
    Generate English sound clip from text.

    Args:
        english (str): Cantonese characters
        filename (str): filepath where audio file is generated
    """
    tts = gTTS(english, lang='en', tld='us')
    tts.save(filename)

def testing():
    #for testing
    import json
    import os

    if not os.path.exists("tts_test_inputs.json"):
        return

    with open("tts_test_inputs.json", "r",encoding='utf-8') as readfile:
        inputs = json.load(readfile)

    yue = inputs['yue']
    en = inputs['en']

    gen_target_audio(yue,'build/ch_normal.mp3', "yue-HK", voice_speed=1)
    gen_target_audio(yue,'build/ch_slow.mp3', "yue-HK", voice_speed=0.5)
    generate_english(en, 'build/en.mp3')


if __name__ == '__main__':
    testing()