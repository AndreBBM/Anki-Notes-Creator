import bs4
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re
from lib import *

# remover comentários inuteis e traduzir para inglês
# atualizar o README.md

def main():
    #invoke('deleteDecks', decks='test1', cardsToo=True)
    invoke('createDeck', deck='Core 2000')

    deck_name = "Core 2000"         # Deck in which the cards will be added
    best_sentence_length = 1    # Use the shortest sentence as default
    
    kanjis = read_words()
    for kanji in kanjis:
        expression, reading, sentence_kana, sentence_en = get_japanese_sentence(kanji, best_sentence_length)

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


