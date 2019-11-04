
import csv  
import json  
import os
import requests
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta,date
import pandas as pd
import glob


path = os.getcwd()

#Dolar
dolar = glob.iglob(path + '/vitorAvaliacao/Avalicao/vitorPazzotti/crawler_dolar/*.csv')
col = []
for filedolar in dolar:
    df2 = pd.read_csv(filedolar, index_col=None, header=0)
    val = df2['value'].values[0]
    del df2['timestamp']
dol = df2.to_csv(path +'/vitorAvaliacao/Avalicao/dol.csv')

#Crypto
all_files = glob.iglob(path + '/vitorAvaliacao/Avalicao/vitorPazzotti/crawler_crypto/*.csv')
print(all_files)

li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

df = pd.concat(li, axis=0, ignore_index=True)
del df['marketCap']
del df['change7D']
del df['totalVolume']
df.to_csv(path +'/vitorAvaliacao/Avalicao/juncao.csv')

#Adicionando coluna priceReal com os valores desejados
r = open(path + '/vitorAvaliacao/Avalicao/juncao.csv')
lines = r.readlines()[1:]
result = []
for teste in lines:
    pos = teste.split(',')[3].replace('"', '')
    conta = float(pos) * val
    result.append(conta)

df.insert(3 , 'priceReal', result)
df.to_csv(path +'/vitorAvaliacao/Avalicao/juncao.csv', index=False)


yesterday = date.today() - timedelta(days=1)
yesterday.strftime('%Y-%m-%d')
f = open( path +'/vitorAvaliacao/Avalicao/juncao.csv', 'rU' )  
reader = csv.DictReader( f, fieldnames = ( "code","name","priceUSD","priceReal","change24H", "symbol", "priceBTC", "volume24H", "timestamp" ))  
out = json.dumps( [ row for row in reader ] )  
print ("JSON parsed!")  

f = open( path +f'/vitorAvaliacao/Avalicao/{yesterday}.json', 'w')  

f.write(out)

print ("JSON saved!")  

data = datetime.today().strftime('%Y-%m-%d')


###ElasticSearch
directory = path + '/vitorAvaliacao/Avalicao/'
res = requests.get('http://localhost:9200')

indexacao = f'cotacao-cripto-{data}'
es = Elasticsearch([{'host' : 'localhost', 'port': '9200'}])

es.indices.create(index=indexacao)
settings = {
    "index_patterns":["cotacao-cripto-*"],
    "settings": {
        "index" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "aliases": {"cotacao-cripto":  {}
    },
    "mappings" : {
        "doc" : {
            "properties" : {
                "code" : {"type" : "keyword"},
                "name" : {"type" : "string"},
                "priceUSD" : {"type" : "integer"},
                "priceReal" : {"type" : "integer"},
                "change24H" : {"type" : "integer"},
                "symbol" : {"type" : "string"},
                "priceBTC" : {"type" : "integer"},
                "volume24H" : {"type" : "keyword"},
                "timestamp" : {"type" : "date"}
                }
            }
        }
    }
}


es.indices.put_alias(index= indexacao, name='cotacao-cripto')
es.indices.update_aliases({
    "actions": [
        {'add' : {"index" : "cotacao-cripto-*", "alias" : "cotacao-cripto"
        }}
    ]
})

for filename in os.listdir(directory):
    if filename.endswith(".json"):
        f = open(path + f'/vitorAvaliacao/Avalicao/{filename}')
        content = f.read()
        for cont in json.loads(content):
            es.index(index=indexacao, body=cont)
print("Done Json inserted on elastic index !")