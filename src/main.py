from lib import *

def main():
    driver = create_driver()
    deck_name = "test"
    invoke('createDeck', deck=deck_name)
    new_cards_info = read_words()
    
    for card_info in new_cards_info:
        try:
            if card_info[0] == "w": # word card - get a sentence from a database and the word definition from weblio
                word = card_info[1]
                expression, reading, sentence_kana, sentence_en = get_japanese_sentence_massif(word, best_sentence_length=25, driver=driver)
                leitura, definicoes = get_definition_weblio(word)
                invoke_card_massif(deck_name, word, expression, reading, sentence_kana, sentence_en, leitura, definicoes)

            elif card_info[0] == "s": # simple sentence card - just translate the sentence
                word = card_info[1]
                translated = translate_sentence(word, dest='en')
                invoke_card_simple_sentence(deck_name, word, word, "", "", translated, "", "")

            elif card_info[0] == "sw": # sentence with word card - get the word definition from weblio from a given sentence
                word = card_info[2]
                sentence = card_info[1]
                leitura, definicoes = get_definition_weblio(word)
                invoke_card_sentence_with_word(deck_name, word, sentence, leitura, definicoes)

            print("Added the word " + word + " to deck " + deck_name)
        except Exception as e:
            print(f"Error processing word {word}: {e}")
    driver.quit()

if __name__ == "__main__":
    main()