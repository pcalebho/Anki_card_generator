import gspread
import os
import shutil
import pandas as pd
from pathlib import Path
from text_to_speech import generate_english, generate_cantonese
from ankipandas import Collection


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



if __name__ == '__main__':
    deck_name = 'Test Deck'
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
      
    #create english files
    list(map(generate_english, list(df_filtered['English Phrase']), en_filenames))

    col = Collection('C:/Users/ttrol/AppData/Roaming/Anki2')

    raw_df = col.cards
    target_deck = raw_df[raw_df['cdeck'] == 'Test Deck']
    notes_df = col.notes

    nid_list = list(target_deck['nid'])
    print(nid_list)
    target_notes = notes_df[notes_df.index.isin(nid_list)]
    print(target_notes)