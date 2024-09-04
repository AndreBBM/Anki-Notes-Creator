# Anki-Notes-Creator

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

Com o anki aberto, importe o deck "test2.apkg" que está incluido neste repositório. O deck pode ser deletado após a importação, ele serve apenas para criar um modelo correto de card.
Em seguida, execute o arquivo "main.py". Ele criará um deck de teste "test1" e adicionará as palavras do arquivo "palavras_adicionar.txt" como cards.
Para utilizar adicionar as suas palavras ao seu deck, basta mudar a variável "deck_name" para o nome do seu deck e adicionar as palavras no arquivo "palavras_adicionar.txt".

### Observações:

O arquivo "palavras_adicionar.txt" deve ser formatado da seguinte maneira:
```txt
palavra1
palavra2
palavra3
...
```
