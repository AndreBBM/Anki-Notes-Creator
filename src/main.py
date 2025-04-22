from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lib import *

def main():
    deck_name = "Core 2000"
    
    invoke('createDeck', deck=deck_name)

    # Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)

    words = read_words()
    for word in words:
        expression, reading, sentence_kana, sentence_en = get_japanese_sentence_IK(word, best_sentence_length=15, driver=driver)

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

    driver.quit()

if __name__ == "__main__":
    main()


