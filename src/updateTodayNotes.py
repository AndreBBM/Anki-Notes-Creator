import requests
import json

from lib import create_driver, furigana_parser, get_definition_weblio, get_japanese_sentence_massif

ANKI_CONNECT_URL = "http://127.0.0.1:8765"

def invoke(action: str, params: dict = None):
    payload = {
        "action": action,
        "version": 6,
        "params": params or {}
    }
    response = requests.post(ANKI_CONNECT_URL, json=payload)
    result = response.json()
    if result.get("error") is not None:
        raise Exception(f"AnkiConnect error in {action}: {result["error"]}")
    return result["result"]

def get_notes_due_today():
    return invoke("findNotes", {"query": "prop:due=0"})

def get_notes_info(note_ids):
    return invoke("notesInfo", {"notes": note_ids})

def update_note_fields(note_id, fields_updates: dict):
    params = {
        "note": {
            "id": note_id,
            "fields": fields_updates
        }
    }
    return invoke("updateNote", params)

def main():
    try:
        note_ids = get_notes_due_today()
        print(f"Found {len(note_ids)} notes due today.")
        if not note_ids:
            return
        
        notes = get_notes_info(note_ids)
        driver = create_driver()
        update_count = 0
        updatable = 0
        for note in notes[::]:
            note_id = note["noteId"]
            fields = note["fields"]
            target_word = ""
            if "Optimized-Voc-Index" in fields:
                if fields["Optimized-Voc-Index"]["value"].isnumeric() and len(fields["Optimized-Voc-Index"]["value"]) < 9:
                    target_word = fields["Vocabulary-Kanji"]["value"]
                    updatable += 1
                    #print(f"CARDS ORIGINAIS {note_id} target_word: {target_word}")

                elif len(fields["Optimized-Voc-Index"]["value"]) > 9 or len(fields["Vocabulary-Kanji"]["value"]) > 9:
                    print(f"New card already, skipping {fields["Optimized-Voc-Index"]["value"]}, {note_id}")
                    continue
                else:
                    target_word = fields["Vocabulary-Kanji"]["value"]
                    updatable += 1
                    #print(f"CARDS PADRÃO {note_id} target_word: {target_word}")

            elif "Front" in fields:
                target_word = fields["Front"]["value"]
                print(f"CARDS BÁSICOS {note_id} target_word: {target_word}")
                continue
            else:
                print(f"Unknown card type for note {note_id}, skipping.")
                continue

            if fields["Notes"]["value"] != "Updated": # if not updated already
                try:
                    expression, reading, sentence_kana, sentence_en = get_japanese_sentence_massif(target_word, best_sentence_length=25, driver=driver)
                    leitura, definicoes = get_definition_weblio(target_word)
                    fields_to_update = {
                        "Optimized-Voc-Index": target_word,
                        "Vocabulary-Kanji": expression,
                        "Vocabulary-Kana": "".join(leitura),
                        "Vocabulary-Furigana" : expression,
                        "Vocabulary-English": definicoes,
                        "Expression": "",
                        "Reading": furigana_parser(target_word, leitura),
                        "Sentence-Kana": "",
                        "Sentence-English": "",
                        "Notes": "Updated"
                    }
                    update_note_fields(int(note_id), fields_to_update)
                    print(f"    Updated note {note_id} with fields: {target_word}")
                    update_count += 1
                except Exception as e:
                    print(f"Error updating note {note_id} {target_word}: {e}")
            else:
                print(f"Note {target_word} {note_id} already updated, skipping.")

        print(f"Successfully updated {update_count}/{updatable} notes")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

"""
Tipos de card:
    {"Optimized-Voc-Index": {"value": "1729", "order": 0} -> cartas originais do deck esse campo é sempre um número de 1 a 2000
        "Vocabulary-Kanji": {"value": "教授", "order": 1} - identificador de palavra-alvo
    
    {"Front": "起動", "Back": "きどう<div>ativação</div>"} -> Cartas básicas só frente e verso campo front
        "Front": "起動" - identificador de palavra-alvo

    se "Optimized-Voc-Index" tiver mais que 9 caracteres: ignorar, são o modelo novo de carta

    Todas as outras, com uma palavra e menos de 9 char no "Optimized-Voc-Index" 
        "Vocabulary-Kanji": {"value": "教授", "order": 1} - identificador de palavra-alvo

        
"""