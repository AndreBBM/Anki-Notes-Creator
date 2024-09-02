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

## FUNCTIONS ##
# Read "palavras_adicionar.txt" and return a list of words without the newline character
def read_words():
    with open("palavras_adicionar.txt", "r") as f:
        words = f.readlines()
    words = [x.strip() for x in words]
    return words

### Defining necessary functions ###

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

invoke('createDeck', deck='test1')
#result = invoke('deckNames')
#print('got list of decks: {}'.format(result))
#invoke('deleteDecks', decks=['test1'], cardsToo=True)

# source: https://github.com/olsgaard/Japanese_nlp_scripts/blob/master/jp_regex.py
# -*- coding: utf-8 -*-

def remove_unicode_block(unicode_block, string):
	''' removes all chaacters from a unicode block and returns all remaining texts from string argument.
		Note that you must use the unicode blocks defined above, or patterns of similar form '''
	return re.sub(unicode_block, '', string)

def extract_unicode_block(unicode_block, string):
	''' extracts and returns all texts from a unicode block from string argument.
		Note that you must use the unicode blocks defined above, or patterns of similar form '''
	return re.findall(unicode_block, string)

# MELHORIA: colocar o furigana somente após o kanji, e não após o hiragana, pra formatação ficar melhor RESOLVIDO
# MELHORIA: melhorar a tradução de palavras com mais de 1 significado

expression = ''        # この文は例えばです
reading = ''          # この文[ぶん]は例えば[たとえば]です
sentence_kana = ''   # このぶんはたとえばです
sentence_en = ''    # This sentence is an example

def get_japanese_sentence(kanji):
    linkpagina = f'https://jisho.org/search/{kanji}%20%23sentences'
    page = requests.get(linkpagina, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    sentences = soup.find_all('div', class_='sentence_content')
    sentence_size = 1e9
    best_sentence_length = 20


    for i in range(len(sentences)):
        japanese_all_letters = sentences[i].find('ul', class_='japanese_sentence japanese japanese_gothic clearfix')
        
        expression_candidato = '' # この文は例えばです
        reading_candidato = ''    # この文[ぶん]は例えば[たとえば]です
        sentence_kana_candidato = '' # このぶんはたとえばです
        sentence_en_candidato = sentences[i].find('div', class_='english_sentence clearfix').find('span', class_='english').get_text() # This sentence is an example

        for count, l in enumerate(japanese_all_letters):
            if type(l) == bs4.element.NavigableString:  # Se for uma string solta
                expression_candidato += l
                reading_candidato += l
                sentence_kana_candidato += l
            elif type(l) == bs4.element.Tag:   # Se for um kanji com leitura
                if l.find('span', class_='furigana') is not None:   # Se tiver furigana
                    furigana = l.find('span', class_='furigana').get_text()
                    word = l.find('span', class_='unlinked').get_text()
                    expression_candidato += word
                    sentence_kana_candidato += furigana
                    if count == 0:  # Unless it's the first word (?)
                        reading_candidato += word + '[' + furigana + ']'
                    else:   # for some reason, there must be a space before the kanji with furigana for Anki to display it correctly
                        # reading_candidato += ' ' + word + '[' + furigana + ']'
                        reading_candidato += furigana_parser_sentences(word, furigana)
                else:
                    word = l.find('span', class_='unlinked').get_text()
                    expression_candidato += word
                    reading_candidato += word
                    sentence_kana_candidato += word

        if abs(len(expression_candidato) - best_sentence_length) < sentence_size:   # escolher a sentença mais próxima do tamanho desejado
            expression = expression_candidato
            reading = reading_candidato
            sentence_kana = sentence_kana_candidato
            sentence_en = sentence_en_candidato
            sentence_size = abs(len(expression_candidato) - best_sentence_length)

    return expression, reading, sentence_kana, sentence_en

def get_definition(kanji):
    # link_definicao = f'https://jisho.org/word/{kanji}'
    link_definicao = f'https://jisho.org/search/{kanji}'
    page_definicao = requests.get(link_definicao, headers={'User-Agent': 'Mozilla/5.0'})
    soup_definicao = BeautifulSoup(page_definicao.content, 'html.parser')
    if soup_definicao.find('div', class_='concept_light clearfix') == None:
        print(f'Não foi possível encontrar a definição de {kanji}')
        return None, None

    primeira_definicao = soup_definicao.find('div', class_='concept_light clearfix')
    definicao = primeira_definicao.find('div', class_='meaning-definition zero-padding').find_all('span', class_='meaning-meaning')
    varias_definicoes = primeira_definicao.find_all('div', class_='meaning-wrapper')
    leituras = primeira_definicao.find_all('span', class_='furigana')
    definicao = definicao[0].get_text().split(';')

    

    # pega o furigana e coloca em uma lista, para o caso da pralavra que tem kanjis separados
    furigana_separados = []
    for l in leituras:
        x = l.find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                furigana_separados.append(x[j].get_text())
        
    leitura = ""
    definicoes = []
    definicoes_novo = ''

    i = 0
    for defini in varias_definicoes:
        if defini.find('span', class_='meaning-meaning') == None:
            break
        definicoes_novo += defini.find('span', class_='meaning-meaning').get_text() + '/ '
        i += 1
        if i == 3:
            break
    definicoes_novo = definicoes_novo[:-2]

    for d in definicao:
        definicoes.append(d.strip())
        if len(definicoes) == 3:
            break

    for i in range(len(leituras)):
        x = leituras[i].find_all('span', class_='kanji')
        if len(x) > 0:
            for j in range(len(x)):
                leitura += x[j].get_text()

    return furigana_separados, definicoes_novo#definicoes

# Formata a palavra com furigana, para o caso de palavras com kanjis separados, como nas definições
# ele devolve o kanji com o furigana específico; e.g. 片[かた]付[づ]ける
# e isso pode ser bem interessante para o caso de palavras com kanjis separados por hiragana, e.g.　申し込む
def furigana_parser(word, furigana):
    # assign the first kanji to the first furigana, the second kanji to the second furigana, and so on
    word_furigana = ''
    for char in word:
        if re.match(kanji_list, char) and len(furigana) > 0:
            word_furigana += " " + char + '[' + furigana.pop(0) + ']'
        else:
            word_furigana += char
    return word_furigana

# Formata a palavra com furigana para o caso das frases, pois no jisho os furiganas não são separados por kanji no caso de sentenças
# ele devolve tudo junto; e.g. 片付ける[かたづ]
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
        #print('Não foi possível encontrar kanji em', word)
        word_furigana = f" {word}[{furigana}]"
    return word_furigana

#get_definition('おもてなし')

deck_name = "Core 2000"
kanjis = read_words()
# kanjis = ['紫']
for kanji in kanjis:
    expression, reading, sentence_kana, sentence_en = get_japanese_sentence(kanji)

    leitura, definicoes = get_definition(kanji)

    try:    
        invoke('addNote', 
            note= {
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
