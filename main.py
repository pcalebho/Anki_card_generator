import gspread
import os
import shutil
import pandas as pd
from pathlib import Path
from text_to_speech import generate_english, generate_cantonese
from ankipandas import Collection
import re

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

def filename_to_anki(filename):
    result = f"[sound:{filename}]"
    return result

def sentence_to_filename(sentence):
    """Converts an English sentence into a legal filename.

    Args:
        sentence: A string containing the English sentence.

    Returns:
        A string containing the legal filename.
    """
    
    # Replace all spaces with underscores.
    filename = sentence.replace(" ", "_")

    # Remove all special characters, except for letters, numbers, and underscores.
    filename = re.sub(r"[^\w_]", "", filename)

    max_length = 254
    if len(filename) > max_length:
        filename = filename[:max_length]

    # Convert the filename to lowercase.
    filename = filename.lower()

    return filename



if __name__ == '__main__':
    anki_media_folder_location = 'C:/Users/ttrol/AppData/Roaming/Anki2/User 1/collection.media'
    deck_name = 'Cantonese Sentences'
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
    df_filtered = df_filtered[df_filtered['Jyutping'] != '']
    df_filtered = df_filtered[df_filtered['Exclude'] == '']


    check_and_create_directory('build')
    print(df_filtered)

    en_filenames = ['build/' + str(i)+'-en.mp4' for i in range(df_filtered.shape[0])]
    ch_filenames =  ['build/' + str(i)+'-ch.mp4' for i in range(df_filtered.shape[0])]
    google_voice = [True for i in range(len(en_filenames))]
      
    #create audio files
    list(map(generate_english, list(df_filtered['English Phrase']), en_filenames))
    list(map(generate_cantonese, list(df_filtered['Cantonese Phrase']), ch_filenames, google_voice))

    col = Collection('C:/Users/ttrol/AppData/Roaming/Anki2')

    raw_df = col.cards
    notes_df = col.notes

    notes_fld = {
        'English': list(df_filtered['English Phrase']),
        'English Audio': list(map(filename_to_anki,en_filenames)),
        'Cantonese': list(df_filtered['Cantonese Phrase']),
        'Cantonese Audio': list(map(filename_to_anki,ch_filenames)),
        'Jyutping': list(df_filtered['Jyutping']),
        'Add Reverse': list(df_filtered['Add Reverse'])
        }
    
    ntags = [row.split() for row in df_filtered['Tags']]


    added_notes_nid = notes_df.add_notes(
        nmodel='Cantonese Sentences (optional reversed card)',
        nflds=notes_fld,
        ntags=ntags,
        inplace=True
        )
    
    col.write(add=True,modify=True)
    
    # added_cards = raw_df.add_cards(nid=added_notes_nid,cdeck=deck_name)  #type:ignore
    # col.write(modify=True)

    # # print(added_notes_nid)
    # print(added_cards)

    
