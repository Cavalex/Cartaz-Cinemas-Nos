import unicodedata
from requests_html import HTMLSession
from settings import *

# remove acentos das letras
# https://stackoverflow.com/a/517974/7966259
def removeAccentChars(x: str):
    return u"".join([c for c in unicodedata.normalize('NFKD', x) if not unicodedata.combining(c)])

# passa "Braga Parque" para "braga-parque"
# não sabia que outro nome dar à função xD
def toPage(s):
    novoString = ""
    for c in s:
        if c == " ":
            novoString = novoString + "-"
        else:
            novoString = novoString + removeAccentChars(c.lower())
    return novoString

# retorna uma lista com todo os nomes de todos os filmes disponíveis no cartaz do cinema
def parseNomes(r):
    return r.html.find('.search-bar', first=True).text.split("Cinemas")[0].split("\n")[1:][:-1]

# retorna uma lista com todos os links para todos os filmes disponíveis no cartaz do cinema
def parseLinks(r):
    links = r.html.find('.search-bar', first=True).html.split("&#13")[2]
    links = links.split("<li><a class=\"list-item\" href=\"")[1:]
    novosLinks = []
    for link in links:
        novosLinks.append("https://cinemas.nos.pt/" + link.split("\">")[0]) # não consigo modificar o array original por alguma razão

    return novosLinks

# pega numa string que contém todos os cinemas, salas e horários e organiza-os numa lista, retornando-a
def parseCinemas(cinema):
    cinemas = cinema.text.split("\n")
    
    i = len(cinemas) - 1
    while i >= 0:
        if cinemas[i] == "Comprar Bilhete":
            cinemas.remove(cinemas[i])
        elif cinemas[i][0] == "|" and cinemas[i][1] == " " and cinemas[i][2].isnumeric():
            cinemas[i] = cinemas[i][2:]
        i -= 1

    return cinemas

# retorna True se o valor passado for uma hora (não valida se é "válida")
def isHour(texto):
    if len(texto) == 5 and texto[2] == "h":
        if texto[0].isnumeric() and texto[1].isnumeric() and texto[3].isnumeric() and texto[4].isnumeric():
            return True
    return False

# retorna todas as sessões disponíveis no nosso cinema. Se o nome estiver mal, retorna todas as sessões. 
def parseSessoes(cinemas):
    sessoes = []
    for i in range(len(cinemas) - 1):
        if toPage(cinemas[i]) == toPage(cinema): # encontrou o cinema
            sessoes = cinemas[i:]
            break
        i += 1
    
    i = 2
    novasSessoes = []
    if sessoes:
        while True:
            while (i < len(sessoes) - 1):
                if not isHour(sessoes[i]):
                    novasSessoes = sessoes[:i]
                    break
                i += 1
            if toPage(sessoes[i]) == toPage(cinema): # se houver outra linha com o mesmo cinema, ou seja, outra sala:
                i += 2
                continue
            break

    return novasSessoes

def main():
        
    urlCartaz = "https://cinemas.nos.pt/pages/cartaz.aspx"
    urlCinema = f"https://cinemas.nos.pt/cinemas/pages/{toPage(cinema)}.aspx"

    session = HTMLSession()

    # receber uma resposta do site
    r = session.get(urlCinema)
    if r.status_code == 404: # 200 == site foi encontrado, 404 == erro (fomos, p. exemplo, redirecionados)
        r = session.get(urlCartaz)

    print(urlCinema)
    print(r.status_code)

    # nome de cada filme na lista "nomes"
    nomes = parseNomes(r)

    # link de cada filme na lista "links"
    links = parseLinks(r)

    # juntar tudo num tuplo (<nome>, <link>)
    filmes = [(nomes[i], links[i]) for i in range(len(links))]

    # verificar os filmes que estão no cinema passado
    for i, filme in enumerate(filmes):
        r = session.get(filme[1]) # site do filme
        cinemas = r.html.find(".table")

        #cinemas[0] == hoje
        #cinemas[1] == amanhã

        # cinemas, salas e horários organizados nesta lista
        cinemas = parseCinemas(cinemas[0])

        # sessoes para o cinema passado em settings.py
        sessoes = parseSessoes(cinemas) if parseSessoes(cinemas) else []

        print(i, filme[0])
        print(sessoes)

if __name__ == "__main__":
    main()
