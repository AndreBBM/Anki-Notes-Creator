from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import bs4
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re
import random
import csv
from googletrans import Translator

kanji_list = r'[㐀-䶵一-鿋豈-頻,々]'
ascii_char = r'[ -~]'
hiragana_full = r'[ぁ-ゟ]'
katakana_full = r'[=-ヿ]'

def read_words():
    with open("src/add_words.txt", "r", encoding="utf-8") as f:
        words = f.readlines()
    words = [x.strip() for x in words if x.strip() != ""]

    for i in range(len(words)):
        if len(words[i]) >= 9:
            if "(" in words[i] and ")" in words[i]:
                w = re.findall(r'\((.*?)\)', words[i])
                words[i] = words[i].replace("(", "<b>").replace(")", "</b>")
                words[i] = ["sw", words[i], w[0]]  # "sw" for sentence with word
            else:
                words[i] = ["s", words[i]]  # "s" for sentence without word
        else:
            words[i] = ["w", words[i]]  # "w" for word without sentence

    return words

def read_words_csv(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        words = [["w", row[0]] for row in reader if row]
    return words


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def remove_unicode_block(unicode_block, string):    # remove all characters from a unicode block
    return re.sub(unicode_block, '', string)


def extract_unicode_block(unicode_block, string):   # extract all characters from a unicode block
    return re.findall(unicode_block, string)


def filter_japanese_or_number(strings: list[str]) -> list[str]:
    # Regex: starts with a Japanese char (hiragana, katakana, kanji) or number
    pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF0-9\uFF10-\uFF19]')
    
    return [s for s in strings if s and pattern.match(s[0])]


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--use-gl=swiftshader")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=options)


def get_japanese_sentence(kanji, best_sentence_length = 1):
    linkpage = f'https://jisho.org/search/{kanji}%20%23sentences'
    page = requests.get(linkpage, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    sentences = soup.find_all('div', class_='sentence_content')
    sentence_size = 1e9

    expression = ''        # この文は例えばです
    reading = ''          # この文[ぶん]は例えば[たとえば]です
    sentence_kana = ''   # このぶんはたとえばです
    sentence_en = ''    # This sentence is an example

    if len(sentences) == 0:
        return '', '', '', ''

    for i in range(len(sentences)):
        japanese_all_letters = sentences[i].find('ul', class_='japanese_sentence japanese japanese_gothic clearfix')
        expression_possible = ''   # この文は例えばです
        reading_possible = ''      # この文[ぶん]は例えば[たとえば]です
        sentence_kana_possible = ''    # このぶんはたとえばです
        sentence_en_possible = sentences[i].find('div', class_='english_sentence clearfix').find('span', class_='english').get_text()

        for count, l in enumerate(japanese_all_letters):
            if type(l) is bs4.element.NavigableString:
                expression_possible += l
                reading_possible += l
                sentence_kana_possible += l
            elif type(l) is bs4.element.Tag:
                if l.find('span', class_='furigana') != None:
                    furigana = l.find('span', class_='furigana').get_text()
                    word = l.find('span', class_='unlinked')
                    if word != None:
                        word = word.get_text()
                    else:
                        word = 'error'
                    expression_possible += word
                    sentence_kana_possible += furigana
                    if count == 0:
                        reading_possible += word + '[' + furigana + ']'
                    else:   # for some reason, there must be a space before the kanji with furigana for Anki to display it correctly
                        # reading_possible += ' ' + word + '[' + furigana + ']'
                        reading_possible += furigana_parser_sentences(word, furigana)
                else:
                    word = l.find('span', class_='unlinked').get_text()
                    expression_possible += word
                    reading_possible += word
                    sentence_kana_possible += word

        #if kanji not in expression_possible:
        #    continue

        if abs(len(expression_possible) - best_sentence_length) < sentence_size:
            expression = expression_possible
            reading = reading_possible
            sentence_kana = sentence_kana_possible
            sentence_en = sentence_en_possible
            sentence_size = abs(len(expression_possible) - best_sentence_length)

    return expression, reading, sentence_kana, sentence_en


def get_japanese_sentence_IK(kanji, best_sentence_length=15, driver=None):
    url = f'https://www.immersionkit.com/dictionary?keyword={kanji}'
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.top.aligned.content'))
        )
    except TimeoutException:
        print(f"No sentences found for {kanji}")
        return '', '', '', ''

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.find_all('div', class_='top aligned content')

    text_jp = []
    text_en = []

    for i, sentence in enumerate(sentences):
        if i % 2 == 0:
            jp = sentence.find('div', class_='react-contextmenu-wrapper')
            en = sentence.find('div', class_='description')
            if jp and en:
                text_jp.append(jp.text.strip())
                text_en.append(en.text.strip())
            if len(text_jp) >= 5:
                break

    # Selecionar a frase com tamanho mais próximo ao desejado
    best_index = min(
        range(len(text_jp)),
        key=lambda i: abs(len(text_jp[i]) - best_sentence_length)
    )

    expression = text_jp[best_index]
    sentence_en = text_en[best_index]

    return expression, expression, expression, sentence_en


def get_japanese_sentence_massif(kanji, best_sentence_length=15, driver=None):
    url = f'https://massif.la/ja/search?q={kanji}'
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.ID, 'results-list'))
        )
    except TimeoutException:
        print(f"No sentences found for {kanji}")
        return '', '', '', ''

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    sentences = soup.find_all('li', class_='text-japanese')[2:4]
    sentence = random.choice(sentences)
    expression = sentence.find_all('div')[0].encode_contents().decode('utf-8').strip().replace('<em>', '<b>').replace('</em>', '</b>')

    return expression, expression, expression, expression


def get_definition(kanji):
    link_definition = f'https://jisho.org/search/{kanji}'
    page_definition = requests.get(link_definition, headers={'User-Agent': 'Mozilla/5.0'})
    soup_definition = BeautifulSoup(page_definition.content, 'html.parser')
    if soup_definition.find('div', class_='concept_light clearfix') == None:
        print(f'It wasnt possible to find a definition for {kanji}')
        return None, None

    first_definition = soup_definition.find('div', class_='concept_light clearfix')
    definition = first_definition.find('div', class_='meaning-definition zero-padding').find_all('span', class_='meaning-meaning')
    various_definitions = first_definition.find_all('div', class_='meaning-wrapper')
    leituras = first_definition.find_all('span', class_='furigana')
    definition = definition[0].get_text().split(';')

    furigana_separados = []
    for l in leituras:
        x = l.find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                furigana_separados.append(x[j].get_text())

        else:
            x = l.find_all('rt')
            if len(x) > 0:
                for j in range(len(x)):
                    furigana_separados.append(x[j].get_text())

    leitura = ""
    definitions = []
    definitions_new = ''

    i = 0
    for defini in various_definitions:
        meaning_meaning = defini.find('span', class_='meaning-meaning')

        if defini.find('span', class_='meaning-meaning') == None:
            break
        
        if "【" in meaning_meaning.get_text() or "】" in meaning_meaning.get_text():
            continue

        definitions_new += meaning_meaning.get_text() + "<br>"
        i += 1
        if i == 3:
            break
    definitions_new = definitions_new[:-4]

    for d in definition:
        definitions.append(d.strip())
        if len(definitions) == 3:
            break

    for i in range(len(leituras)):
        x = leituras[i].find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                leitura += x[j].get_text()
    return furigana_separados, definitions_new


def get_definition_weblio(kanji):
    link_definition = f'https://www.weblio.jp/content/{kanji}'
    page_definition = requests.get(link_definition, headers={'User-Agent': 'Mozilla/5.0'})
    soup_definition = BeautifulSoup(page_definition.content, 'html.parser')
    if soup_definition.find('div', class_='pbarTLW') == None:
        print(f'It wasnt possible to find a definition for {kanji}')
        return None, None
    
    furigana_jisho, w = get_definition(kanji)
    all_definitions = soup_definition.find_all('div', class_='Sgkdj')
    for d in all_definitions:
        definition_each = d.find_all('p')
        reading_each = definition_each[0].get_text().split('読み方：')[1]
        if reading_each != ''.join(furigana_jisho):
            print(f"Different readings found for {kanji}: {reading_each} (weblio) and {''.join(furigana_jisho)} (jisho)")    
            continue
        else:
            print(f"Same reading found for {kanji}: {reading_each} (weblio) and {''.join(furigana_jisho)} (jisho)")
            various_definitions = definition_each[1:]
            various_definitions_text = [d.get_text() for d in various_definitions if d.get_text() != '']
            various_definitions_text = various_definitions_text[:3]  # Limit to 3 definitions
            definitions_for_anki = ''
            for d in various_definitions_text:
                definitions_for_anki += f"{d}\n" + "<br>"
            return [reading_each], definitions_for_anki
        
    # If no matching reading found, return the first definition from weblio
    definitions_for_anki = ''
    if soup_definition.find('div', class_='Sgkdj') != None:
        first_definition = soup_definition.find('div', class_='Sgkdj')
        definition = first_definition.find_all('p')
        reading_each = definition[0].get_text().split('読み方：')[1]
        various_definitions = definition[1:]
        various_definitions_text = [d.get_text() for d in various_definitions if d.get_text() != '']
        various_definitions_text = various_definitions_text[:3]  # Limit to 3 definitions
    elif soup_definition.find('div', class_='Jtnhj') != None:
        first_definition = soup_definition.find('div', class_='Jtnhj')
        definition = first_definition.text.split('\n')
        various_definitions = [d for d in definition if d != '']
        reading_each = various_definitions[0].split('読み方：')[1]
        various_definitions_text = various_definitions[1:2]
    for d in various_definitions_text:
        definitions_for_anki += f"{d}\n" + "<br>"
    return [reading_each], definitions_for_anki


# Format the word with furigana, for the case of words with separated kanjis, as in definitions
# it returns the kanji with the specific furigana; e.g. 片[かた]付[づ]ける
def furigana_parser(word, furigana):
    if len(furigana) == 1:
        return f" {word}[{furigana[0]}]"
    # assign the first kanji to the first furigana, the second kanji to the second furigana, and so on
    word_furigana = ''
    for char in word:
        if re.match(kanji_list, char) and len(furigana) > 0:
            word_furigana += " " + char + '[' + furigana.pop(0) + ']'
        else:
            word_furigana += char
    return word_furigana


def translate_sentence(text, src='auto', dest='en'):
    import asyncio
    from googletrans import Translator

    async def _translate():
        translator = Translator()
        translation = await translator.translate(text, src=src, dest=dest)
        return translation.text

    return asyncio.run(_translate())


# Format the word with furigana, for the case of sentences, because in jisho the furiganas are not separated by kanji in the case of sentences
# it returns everything together; e.g. 片付ける[かたづ]
def furigana_parser_sentences(word, furigana):
    word_furigana = ''
    furigana = furigana.replace(' ', '')
    word = word.replace(' ', '')
    if len(furigana) == 0:
        return word
    if any(re.findall(kanji_list, word)):
        first_kanji = re.search(kanji_list, word).group()
        last_kanji = re.search(kanji_list, word[::-1]).group()[::-1]
        first_kanji_index = word.index(first_kanji)
        last_kanji_index = len(word) - word[::-1].index(last_kanji) - 1
        word_furigana = " " + word[:first_kanji_index] + word[first_kanji_index:last_kanji_index+1] + "[" + furigana + "]" + word[last_kanji_index+1:]
    else:
        word_furigana = f" {word}[{furigana}]"
    return word_furigana


def invoke_IK(deck_name, word, expression, reading, sentence_kana, sentence_en, leitura, definicoes):
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
                "Notes": "Updated"
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


def invoke_card_massif(deck_name, word, expression, reading, sentence_kana, sentence_en, leitura, definicoes):
    invoke('addNote',
        note={
            "deckName": deck_name,
            "modelName": "Core 2000",
            "fields": {
                'Optimized-Voc-Index': word,
                'Vocabulary-Kanji': expression,
                'Vocabulary-Kana': ''.join(leitura),
                'Vocabulary-Furigana' : expression,
                'Vocabulary-English': definicoes,
                'Expression': "",
                'Reading': furigana_parser(word, leitura),
                'Sentence-Kana': "",
                'Sentence-English': "",
                "Notes": "Updated"
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


def invoke_card_simple_sentence(deck_name, word, expression, reading, sentence_kana, sentence_en, leitura, definicoes):
    invoke('addNote',
        note={
            "deckName": deck_name,
            "modelName": "Core 2000",
            "fields": {
                'Optimized-Voc-Index': word,
                'Vocabulary-Kanji': expression,
                'Vocabulary-Kana': "",
                'Vocabulary-Furigana' : expression,
                'Vocabulary-English': "",
                'Expression': "",
                'Reading': "",
                'Sentence-Kana': "",
                'Sentence-English': sentence_en,
                "Notes": "Updated"
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


def invoke_card_sentence_with_word(deck_name, word, expression, leitura, definicoes):
    invoke('addNote',
        note={
            "deckName": deck_name,
            "modelName": "Core 2000",
            "fields": {
                'Optimized-Voc-Index': word,
                'Vocabulary-Kanji': expression,
                'Vocabulary-Kana': ''.join(leitura),
                'Vocabulary-Furigana' : expression,
                'Vocabulary-English': definicoes,
                'Expression': "",
                'Reading': furigana_parser(word, leitura),
                'Sentence-Kana': "",
                'Sentence-English': "",
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

