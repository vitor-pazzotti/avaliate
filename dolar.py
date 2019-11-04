import requests
from datetime import datetime
import csv
import os
import time

path = os.getcwd()

def moeda(html):

	aux = html.find("instrumentH1inlineblock") + 30

	tipo_moeda = html[aux:aux+31]

	return tipo_moeda

def cotacao(html):

	aux = html.find("lastInst pid-2103-last") + 30

	cot = html[aux:aux+29].strip()

	return cot

def mudanca(html):

	aux = html.find("pid-2103-pc") + 30

	mud = html[aux:aux+20].strip()

	return mud;

def percentual(html):

	aux = html.find("pid-2103-pcp") + 30

	perc = html[aux:aux+10].strip()

	return perc

def timestamp(r):
    now = datetime.now()
    time = datetime.timestamp(now)

    return time

def gravar(saida):
    now = datetime.now()
    
    time = datetime.date(now)

    arq = csv.writer(open(path + '/crawler_dolar/dolar_{}.csv'.format(time), '+a'), delimiter = ',')

    if os.stat(path + '/crawler_dolar/dolar_{}.csv'.format(time)).st_size == 0:
        arq.writerow(['currency', 'value', 'change', 'perc', 'timestamp'])

    arq.writerow(saida)

def main():
	r = requests.get(url="https://m.investing.com/currencies/usd-brl", headers={'User-Agent':'curl/7.52.1'})

	html = r.text

	saida = [moeda(html), cotacao(html), mudanca(html), percentual(html), timestamp(r)]

	gravar(saida)


main()