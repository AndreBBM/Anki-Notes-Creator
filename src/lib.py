import bs4
from bs4 import BeautifulSoup
import requests
import json
import urllib.request
import re

kanji_list = r'[㐀-䶵一-鿋豈-頻,々]'
ascii_char = r'[ -~]'
hiragana_full = r'[ぁ-ゟ]'
katakana_full = r'[=-ヿ]'

# Read "add_words.txt" and return a list of words without the newline character
def read_words():
    with open("src/add_words.txt", "r", encoding="utf-8") as f:
        words = f.readlines()
    words = [x.strip() for x in words]
    return words

# source: https://github.com/olsgaard/Japanese_nlp_scripts/blob/master/jp_regex.py
# Defining necessary functions #

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

def get_japanese_sentence(kanji):
    linkpage = f'https://jisho.org/search/{kanji}%20%23sentences'
    page = requests.get(linkpage, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    sentences = soup.find_all('div', class_='sentence_content')
    sentence_size = 1e9
    best_sentence_length = 20

    for i in range(len(sentences)):
        japanese_all_letters = sentences[i].find('ul', class_='japanese_sentence japanese japanese_gothic clearfix')
        expression_possible = ''   # この文は例えばです
        reading_possible = ''      # この文[ぶん]は例えば[たとえば]です
        sentence_kana_possible = ''    # このぶんはたとえばです
        sentence_en_possible = sentences[i].find('div', class_='english_sentence clearfix').find('span', class_='english').get_text()

        for count, l in enumerate(japanese_all_letters):
            if type(l) is bs4.element.NavigableString:  # Se for uma string solta # if goes wrong change is to ==
                expression_possible += l
                reading_possible += l
                sentence_kana_possible += l
            elif type(l) is bs4.element.Tag:   # Se for um kanji com leitura # if goes wrong change is to ==
                if l.find('span', class_='furigana') != None:   # Se tiver furigana
                    furigana = l.find('span', class_='furigana').get_text()
                    word = l.find('span', class_='unlinked').get_text()
                    expression_possible += word
                    sentence_kana_possible += furigana
                    if count == 0:  # Unless it's the first word (?)
                        reading_possible += word + '[' + furigana + ']'
                    else:   # for some reason, there must be a space before the kanji with furigana for Anki to display it correctly
                        # reading_possible += ' ' + word + '[' + furigana + ']'
                        reading_possible += furigana_parser_sentences(word, furigana)
                else:
                    word = l.find('span', class_='unlinked').get_text()
                    expression_possible += word
                    reading_possible += word
                    sentence_kana_possible += word

        if abs(len(expression_possible) - best_sentence_length) < sentence_size:   # escolher a sentença mais próxima do tamanho desejado
            expression = expression_possible
            reading = reading_possible
            sentence_kana = sentence_kana_possible
            sentence_en = sentence_en_possible
            sentence_size = abs(len(expression_possible) - best_sentence_length)

    return expression, reading, sentence_kana, sentence_en

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

    # place furigana in a list, for the case of words with separated kanjis
    furigana_separados = []
    for l in leituras:
        x = l.find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                furigana_separados.append(x[j].get_text())

    leitura = ""
    definitions = []
    definitions_new = ''

    i = 0
    for defini in various_definitions:
        if defini.find('span', class_='meaning-meaning') == None:
            break
        definitions_new += defini.find('span', class_='meaning-meaning').get_text() + '/ '
        i += 1
        if i == 3:
            break
    definitions_new = definitions_new[:-2]

    for d in definition:
        definitions.append(d.strip())
        if len(definitions) == 3:
            break

    for i in range(len(leituras)):
        x = leituras[i].find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                leitura += x[j].get_text()

    return furigana_separados, definitions_new#definitions


# Format the word with furigana, for the case of words with separated kanjis, as in definitions
# it returns the kanji with the specific furigana; e.g. 片[かた]付[づ]ける
# and this can be very interesting for the case of words with kanjis separated by hiragana, e.g. 申し込む
def furigana_parser(word, furigana):
    # assign the first kanji to the first furigana, the second kanji to the second furigana, and so on
    word_furigana = ''
    for char in word:
        if re.match(kanji_list, char) and len(furigana) > 0:
            word_furigana += " " + char + '[' + furigana.pop(0) + ']'
        else:
            word_furigana += char
    return word_furigana


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