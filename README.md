# Anki-Notes-Creator

## Objective:

This project aims to facilitate the creation of flashcards for the Anki memorization software. The Anki Notes Creator automatically generates cards from a text file containing only the desired target words. **Using just the desired word, the cards are created with the word and an example sentence on the front, and the translation of both on the back, along with the pronunciation of each ideogram and links to online dictionaries for the word.**
![Front](card_front.png)
![Back](card_back.png)

### Requirements:

To run this project, you need to have Anki installed, in any version, and Anki-Connect, with a version compatible with the installed Anki.

To install Anki:
https://apps.ankiweb.net/

To install Anki-Connect:
https://foosoft.net/projects/anki-connect/

### How to use:

With Anki open, import the "card_model.apkg" deck included in this repository. The deck can be deleted after importing; it only serves to create a correct card template.
Next, run the "main.py" file. It will create a test deck "test1" and add the words from the "add_words.txt" file as cards.
To add your words to your deck, simply change the "deck_name" variable to the name of your deck and add the words to the "add_words.txt" file.

### Notes:

The "add_words.txt" file should be formatted as follows:
```txt
word1
word2
word3
...
```

## Português

## Objetivo:

Esse projeto tem o intuito de facilitar a criação de cards para o software de memorização Anki. O Anki Notes Creator cria cards de maneira automática a partir de um arquivo de texto apenas com as palavras alvo desejadas. **A partir apenas da palavra desejada, os cards são criados com a palavra e uma frase de exemplo na frente, e a tradução de ambas na parte de trás junto com a pronúncia de cada ideograma e links para dicionários online para a palavra.**
![Frente](card_front.png)
![Verso](card_back.png)

### Requerimentos:

Para rodar esse projeto, é necessário que se tenha instalado Anki, em qualquer versão, e o Anki-Connect, com versão compatível com o Anki instalado.

Para instalar o Anki:
https://apps.ankiweb.net/

Para instalar o Anki-Connect:
https://foosoft.net/projects/anki-connect/

### Como usar:

Com o anki aberto, importe o deck "card_model.apkg" que está incluido neste repositório. O deck pode ser deletado após a importação, ele serve apenas para criar um modelo correto de card.
Em seguida, execute o arquivo "main.py". Ele criará um deck de teste "test1" e adicionará as palavras do arquivo "add_words.txt" como cards.
Para utilizar adicionar as suas palavras ao seu deck, basta mudar a variável "deck_name" para o nome do seu deck e adicionar as palavras no arquivo "add_words.txt".

### Observações:

O arquivo "add_words.txt" deve ser formatado da seguinte maneira:
```txt
palavra1
palavra2
palavra3
...
```
