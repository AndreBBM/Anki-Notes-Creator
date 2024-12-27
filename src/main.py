import bs4
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re
from lib import *

def main():
    deck_name = "test1"    

    invoke('createDeck', deck=deck_name)

    best_sentence_length = 1    # Use the shortest sentence as default
    
    words = read_words()
    for word in words:
        expression, reading, sentence_kana, sentence_en = get_japanese_sentence(word, best_sentence_length)

        leitura, definicoes = get_definition(word)

        try:
            invoke('addNote',
            note={
                "deckName": deck_name,
                "modelName": "Core 2000",
                "fields": {
                    'Optimized-Voc-Index': word,
                    'Vocabulary-Kanji': word,
                    'Vocabulary-Kana': ''.join(leitura),
                    'Vocabulary-Furigana' : furigana_parser(word, leitura),
                    'Vocabulary-English': definicoes,
                    'Expression': expression,
                    'Reading': reading,
                    'Sentence-Kana': sentence_kana,
                    'Sentence-English': sentence_en,
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": deck_name,
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
            }
        )

            print("Added the word " + word + " to deck " + deck_name)
        except Exception as e:
            print(e)
            print("Error trying to add " + word + " to deck " + deck_name)
            continue

if __name__ == "__main__":
    main()


