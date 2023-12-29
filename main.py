import gspread
import os
import shutil
import pandas as pd
from pathlib import Path
from text_to_speech import generate_english, generate_cantonese
from ankipandas import Collection
import re
import datetime
import click
from dotenv import load_dotenv

load_dotenv()
ANKI_MEDIA_LOCATION = os.environ.get('ANKI_MEDIA_LOCATION')
ANKI_LOCATION = os.environ.get('ANKI_LOCATION')
GOOGLE_SHEET_KEY = os.environ.get('GOOGLE_SHEET_KEY')


def check_and_create_directory(path):
    """
    Checks if a file directory exists and creates it if it does not.

    Args:
        path: The path to the directory to check.
    """

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)

def filename_to_anki(filename):
    """
    Creates audio filename for anki syntax
    """
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

    max_length = 249
    if len(filename) > max_length:
        filename = filename[:max_length]

    # Convert the filename to lowercase.
    filename = filename.lower()

    return filename

def main():
    anki_media_folder_location = ANKI_MEDIA_LOCATION

    # Open the Google Sheet
    gc = gspread.service_account(Path('google_auth.json'))
    sheet = gc.open_by_key(GOOGLE_SHEET_KEY)          #google sheet must be public to view and edit

    if anki_media_folder_location is None:
        return

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
    df_filtered['Cantonese Phrase'] = [" ".join(phrase.split()) for phrase in df_filtered['Cantonese Phrase']] 

    filtered_index = list(df_filtered.index.values)

    # check_and_create_directory('build')
    print(df_filtered)
    print("Entries Adding: ", df_filtered.shape[0])

    #CLI confirmation
    if not click.confirm('Add notes?'):
        return
    if not click.confirm('Is Anki closed?'):
        return
    
    #Create filepaths 
    en_filenames = [sentence_to_filename(phrase)+'-en.mp3' for phrase in list(df_filtered['English Phrase'])]
    ch_filenames =  [sentence_to_filename(phrase) + '-ch.mp3' for phrase in list(df_filtered['Jyutping'])]
    chs_filenames =  [sentence_to_filename(phrase) + '-chs.mp3' for phrase in list(df_filtered['Jyutping'])]
    en_path = [anki_media_folder_location +'/' + f for f in en_filenames]
    ch_path = [anki_media_folder_location +'/' + f for f in ch_filenames]
    chs_path = [anki_media_folder_location +'/' + f for f in chs_filenames]


    #create audio files
    list(map(generate_english, list(df_filtered['English Phrase']), en_path))
    list(map(generate_cantonese, list(df_filtered['Cantonese Phrase']), ch_path))
    list(map(generate_cantonese, list(df_filtered['Cantonese Phrase']), chs_path, [0.5]*len(en_path)))

    #Add notes to Anki collection
    col = Collection(ANKI_LOCATION)
    notes_df = col.notes
    notes_fld = {
        'English': list(df_filtered['English Phrase']),
        'English Audio': list(map(filename_to_anki,en_filenames)),
        'Cantonese': list(df_filtered['Cantonese Phrase']),
        'Cantonese Audio': list(map(filename_to_anki,ch_filenames)),
        'Cantonese Audio Slow': list(map(filename_to_anki,chs_filenames)),
        'Jyutping': list(df_filtered['Jyutping']),
        'Notes': list(df_filtered['Notes']),
        'Front Note': list(df_filtered['Front Note']),
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
    

    col = Collection(ANKI_LOCATION)
    
    #Find newly added notes and add to database
    cards = col.cards

    #Only adds cards if notes were added. 
    if isinstance(added_notes_nid, list) and all(isinstance(item, int) for item in added_notes_nid):
        #cord is the template value
        added_cards = cards.add_cards(nid=added_notes_nid, cdeck='Cantonese Sentences', inplace=True, cord=0)


    col.summarize_changes()
    col.write(add=True,modify=True)

    #Update exclude column with time card is was added
    current_time = datetime.datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
    for i in filtered_index:
        worksheet.update_cell(i+2,1,time_string)

def validate_setup():
    """
    This function validates if authentication and environment is correctly setup.
    """
    error = False
    if ANKI_LOCATION is None:
        print("Missing 'ANKI_LOCATION' env variable")
        error = True
    if ANKI_MEDIA_LOCATION is None:
        print("Missing 'ANKI_MEDIA_LOCATION' env variable")
        error = True
    if GOOGLE_SHEET_KEY is None:
        print("Missing 'GOOGLE_SHEET_KEY' env variable")
        error = True
    if not os.path.exists('google_auth.json'):
        print("Missing 'google_auth.json' file in root of project")
        error = True

    if error:
        raise FileNotFoundError
    
if __name__ == '__main__':
    validate_setup()
    
    try:
        main()
    except Exception: 
        print("Error Running")

    input('Enter to continue: ')
    

    
