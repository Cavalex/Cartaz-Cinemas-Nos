# Cartaz-Cinemas-Nos
Aplicação que envia regularmente uma notificação ao utilizador com todos os filmes disponíveis no cartaz dos cinemas Nos.
Só funciona com os cinemas que se encontram na lista de cinemas dest site: https://cinemas.nos.pt/pages/cartaz.aspx

Atenção, de momento as notificações só funcionam em Windows. Em Mac ou Linux é preciso abrir manualmente o ficheiro com os horários dos filmes.

## Como correr o programa
Para correr o programa, primeiro precisamos de instalar as bibliotecas que estão em *requirementes*
```
pip install -r requirements.txt
```
Depois é só fazer:
```
python main.py # Windows
```
Para fazer o programa correr automaticamente sempre que ligam o pc (em Windows, e não gasta CPU), sigam este tutorial: 
https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd
