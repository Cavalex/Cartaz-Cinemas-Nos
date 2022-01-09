import unicodedata
import time
import platform
import os
from datetime import datetime
from win10toast_click import ToastNotifier
from requests_html import HTMLSession
from settings import *

# remove acentos das letras
# https://stackoverflow.com/a/517974/7966259
def removerAcentos(x: str):
    return u"".join([c for c in unicodedata.normalize('NFKD', x) if not unicodedata.combining(c)])

# passa "Braga Parque" para "braga-parque"
# não sabia que outro nome dar à função xD
def simplificarNome(s):
    novoString = ""
    for c in s:
        if c == " ":
            novoString = novoString + "-"
        else:
            novoString = novoString + removerAcentos(c.lower())
    return novoString

# retorna o nome do filme para o site com o filme
def parseNome(r):
    #return r.html.find('.search-bar', first=True).text.split("Cinemas")[0].split("\n")[1:][:-1]
    return r.html.find("h1", first=True)

# retorna uma lista com todos os links para todos os filmes disponíveis no cartaz do cinema
def parseLinks(r):
    links = r.html.find('.search-bar', first=True).html.split("&#13")[2]
    links = links.split("<li><a class=\"list-item\" href=\"")[1:]
    novosLinks = []
    for link in links:
        novosLinks.append("https://cinemas.nos.pt" + link.split("\">")[0]) # não consigo modificar o array original por alguma razão

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
def serHora(texto):
    if len(texto) == 5 and texto[2] == "h":
        if texto[0].isnumeric() and texto[1].isnumeric() and texto[3].isnumeric() and texto[4].isnumeric():
            return True
    return False

# organiza as horas do cinema por ordem crescente
def organizarHoras(horas):
    format = "%Hh%M"
    timeHoras = [time.strptime(h, format) for h in horas]
    return [time.strftime(format, h) for h in sorted(timeHoras)]

# retorna todas as sessões disponíveis no nosso cinema. Se o nome estiver mal, retorna todas as sessões. 
def parseSessoes(cinemas):
    sessoes = []
    for i in range(len(cinemas) - 1):
        if simplificarNome(cinemas[i]) == simplificarNome(cinema): # encontrou o cinema
            sessoes = cinemas[i:]
            break
        i += 1
    
    i = 2
    z = i
    novasSessoes = []
    if sessoes:
        while True:
            while (i < len(sessoes) - 1):
                if not isHour(sessoes[i]):
                    novasSessoes.append(sessoes[z:i])
                    break
                i += 1
            if simplificarNome(sessoes[i]) == simplificarNome(cinema): # se houver outra linha com o mesmo cinema, ou seja, outra sala:
                i += 2
                z = i
                continue
            break

    return organizarHoras(sum(novasSessoes, []))

# envia uma notificação para o pc da pessoa
# só funciona em windows
def enviarNotificacao():
    toaster = ToastNotifier()
    toaster.show_toast(
        title=f"Filmes Cinema {cinema}",
        msg=f"{cinema}: carrega para veres todos os filmes disponíveis lá! >>", # message 
        icon_path=f"{os.getcwd()}\\icon.ico",
        duration = 5,
        callback_on_click=abrirFicheiro # click notification to run function 
    )

    print(f"{os.getcwd()}\\icon.ico")

# abre o ficheiro ao carregar na notificação
def abrirFicheiro():
    os.system(f"{nomeFicheiro}")

# vai retornar True se já tiver passado mais que o tempo suficiente para enviar nova notificaçao
def horaDeEnviarNotificacao(ultimaAtualizacao):
    format = "%H:%M %d-%m-%Y"
    ultimaNotificacao = datetime.strptime(ultimaAtualizacao[:-1], format) # sem o [:-1] dá "ValueError: unconverted data remains" no strptime
    agora = datetime.now()
    diferenca = agora - ultimaNotificacao
    horas = diferenca.days * 24

    if horas >= intervaloDeTempo:
        with open(nomeFicheiro, "w") as ficheiro:
            ultimaAtualizacao = datetime.strftime(agora, format)
            ficheiro.write(ultimaAtualizacao)
            ficheiro.write("\n\n")
        return True
    return False

# guarda todas as sessões de todos os filmes do cinema num ficheiro
def guardarSessoesEmFicheiro():

    urlCartaz = "https://cinemas.nos.pt/pages/cartaz.aspx"
    urlCinema = f"https://cinemas.nos.pt/cinemas/pages/{simplificarNome(cinema)}.aspx"

    session = HTMLSession()

    # receber uma resposta do site
    r = session.get(urlCinema)
    if r.status_code == 404: # 200 == site foi encontrado, 404 == erro (fomos, p. exemplo, redirecionados)
        r = session.get(urlCartaz)
    print(urlCinema)

    # link de cada filme na lista "links"
    links = parseLinks(r)

    with open("sessoes.txt", "a") as ficheiro:
        
        ficheiro.write(f"Filmes Disponíveis em: {cinema}\n")

        # verificar os filmes que estão no cinema no dia de hoje
        for link in links:
            r = session.get(link) # site do filme
            cinemas = r.html.find(".table")

            nome = parseNome(r).text

            #cinemas[0] == hoje
            #cinemas[1] == amanhã, etc

            # cinemas, salas e horários organizados nesta lista
            cinemas = parseCinemas(cinemas[0])

            # sessoes para o cinema passado em settings.py
            sessoes = parseSessoes(cinemas) if parseSessoes(cinemas) else []

            if sessoes:
                ficheiro.write(f"\n{nome}:\n")
                for i in range(len(sessoes)):
                    if i == len(sessoes) - 1:
                        ficheiro.write(sessoes[i] + "\n")
                    else:
                        ficheiro.write(sessoes[i] + ",")

    print("-- Sessões atualizadas! --")

def main():
    
    ultimaAtualizacao = None
    with open(nomeFicheiro, "r") as ficheiro:
        ultimaAtualizacao = ficheiro.readline() # a 1ª linha do ficheiro
    print(f"-- {ultimaAtualizacao[:-1]} --") # para não fazer um \n estranho

    while True:
        if horaDeEnviarNotificacao(ultimaAtualizacao):
            guardarSessoesEmFicheiro()

            sistema = platform.system().lower()
            if sistema == "windows": # só funciona em windows
                enviarNotificacao()
        print("-- esperar 1 hora --")
        time.sleep(3600000) # esperar 1 hora para o loop não estar sempre a correr

if __name__ == "__main__":
    main()
