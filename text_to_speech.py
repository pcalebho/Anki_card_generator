from gtts import gTTS
from google.cloud import texttospeech
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('google_auth.json')

def generate_cantonese(cantonese, filename, voice_speed=1.0):
    """
    Generate Cantonese sound clip from text.

    Args:
        cantonese (str): Cantonese characters
        filename (str): filepath where audio file is generated
        voice_speed(float): Speed of audio file
    """
    cantonese = cantonese.replace('?','')

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
    """
    Generate English sound clip from text.

    Args:
        english (str): Cantonese characters
        filename (str): filepath where audio file is generated
    """
    tts = gTTS(english, lang='en', tld='us')
    tts.save(filename)


if __name__ == '__main__':
    #for testing
    import json
    with open("tts_test_inputs.json", "r",encoding='utf-8') as readfile:
        inputs = json.load(readfile)

    yue = inputs['yue']
    en = inputs['en']

    generate_cantonese(yue,'build/ch_normal.mp3', voice_speed=1)
    generate_cantonese(yue,'build/ch_slow.mp3', voice_speed=0.5)
    generate_english(en, 'build/en.mp3')
