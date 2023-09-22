import gspread
import os
import shutil
import pandas as pd
from pathlib import Path
from gtts import gTTS

def check_and_create_directory(path):
    """Checks if a file directory exists and creates it if it does not.

    Args:
        path: The path to the directory to check.
    """

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)


def generate_english(english, filename):
    tts = gTTS(english, lang='en', tld='us')
    tts.save('build/' + filename)


if __name__ == '__main__':
   # Open the Google Sheet
    gc = gspread.service_account(Path('auth.json'))
    sheet = gc.open_by_key('1ljONb-A-wz0DRU7L4BLK_WrCFn76mbKe19DBbOOWQ0U')

    # Get the worksheet
    worksheet = sheet.worksheet('Sheet1')

    # Get the values in the worksheet
    values = worksheet.get_all_values()

    df = pd.DataFrame(values[1:])
    df.columns= values[0]
    df_filtered = df[df['Cantonese Phrase'] != '']
    df_filtered = df_filtered[df_filtered['English Phrase'] != '']


    check_and_create_directory('build')

    en_filenames = [str(i)+'-en.mp4' for i in range(df_filtered.shape[0])]
    print(en_filenames)
    print(list(df_filtered['English Phrase']))
    
    #create english files
    list(map(generate_english, list(df_filtered['English Phrase']), en_filenames))
