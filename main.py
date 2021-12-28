from requests_html import HTMLSession
from settings import *


# passa "Braga Parque" para "braga-parque"
# não sabia que outro nome dar à função xD
def toPage(s):
    novoString = ""
    for c in s:
        if c == " ":
            novoString = novoString + "-"
        else:
            novoString = novoString + c.lower()
    return novoString

urlCartaz = "https://cinemas.nos.pt/pages/cartaz.aspx"
urlCinema = f"https://cinemas.nos.pt/cinemas/pages/{toPage(cinema)}.aspx"

def main():

    session = HTMLSession()

    r = session.get(urlCinema)
    if r.status_code == 404: # a página não foi encontrada
        r = session.get(urlCartaz)
    
    #r = session.get(urlCartaz)
    print(r.status_code)

    # nome de cada filme na lista "nomes"
    nomes = r.html.find('.search-bar', first=True).text.split("Cinemas")[0].split("\n")[1:][:-1]
    #print(nomes)

    # link de cada filme na lista "links"
    links = r.html.find('.search-bar', first=True).html.split("&#13")[2]
    links = links.split("<li><a class=\"list-item\" href=\"")[1:]
    novosLinks = []
    for link in links:
        novosLinks.append("https://cinemas.nos.pt/" + link.split("\">")[0]) # não consigo modificar o array original por alguma razão

    # juntar tudo num tuplo (<nome>, <link>)
    filmes = [(nomes[i], novosLinks[i]) for i in range(len(novosLinks))]

    # verificar os filmes que estão no cinema passado
    filme = filmes[1]
    r = session.get(filme[1])
    cinemas = r.html.find(".table")
    #cinemas[0] # hoje
    #cinemas[1] # amanhã
    print(cinemas[0].text)
    print()




if __name__ == "__main__":
    main()
