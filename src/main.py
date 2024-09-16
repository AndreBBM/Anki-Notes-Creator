import bs4
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re
from lib import *


def main():
    invoke('createDeck', deck='test1')

    expression = ''        # この文は例えばです
    reading = ''          # この文[ぶん]は例えば[たとえば]です
    sentence_kana = ''   # このぶんはたとえばです
    sentence_en = ''    # This sentence is an example

    get_definition('おもてなし')

    deck_name = "test1"
    kanjis = read_words()
    for kanji in kanjis:
        expression, reading, sentence_kana, sentence_en = get_japanese_sentence(kanji)

        leitura, definicoes = get_definition(kanji)

        try:
            invoke('addNote',
            note={
                "deckName": deck_name,
                "modelName": "Core 2000",
                "fields": {
                    'Optimized-Voc-Index': kanji,
                    'Vocabulary-Kanji': kanji,
                    'Vocabulary-Kana': ''.join(leitura),
                    'Vocabulary-Furigana' : furigana_parser(kanji, leitura),
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

            print("Adicionada a palavra " + kanji + " ao deck " + deck_name)
        except Exception as e:
            print(e)
            print("Erro ao adicionar o kanji " + kanji + " ao deck")
            continue

if __name__ == "__main__":
    main()


