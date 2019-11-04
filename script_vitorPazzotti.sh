#!/bin/bash

# sudo apt-get update -y > /dev/null 2>&1
# sudo apt-get install zip unzip -y > /dev/null 2>&1
# sudo apt-get install python3 -y > /dev/null 2>&1
# sudo apt-get install python3-pip -y > /dev/null 2>&1
# pip3 install requests > /dev/null 2>&1
# pip3 install beautifulsoup4 > /dev/null 2>&1
# pip3 install pandas > /dev/null 2>&1




mkdir vitorPazzotti
mkdir vitorPazzotti/bin
mkdir vitorPazzotti/crawler_crypto
mkdir vitorPazzotti/crawler_crypto/processados
mkdir vitorPazzotti/crawler_crypto/consolidados
mkdir vitorPazzotti/crawler_crypto/consolidados/transferidos
mkdir vitorPazzotti/crawler_dolar
mkdir vitorPazzotti/crawler_dolar/transferidos
mkdir vitorPazzotti/processados_json
mkdir vitorPazzotti/processados_json/indexados

sudo chmod -R 777 vitorPazzotti/
#Pasta no HDFS
# hdfs dfs -mkdir /user/vitorPazzotti
# hdfs dfs -mkdir user/vitorPazzotti/input
# hdfs dfs -mkdir /user/vitorPazzotti/input/processados
# hdfs dfs -mkdir /user/vitorPazzotti/input
# hdfs dfs -mkdir /user/vitorPazzotti/output
# hdfs dfs -mkdir /user/vitorPazzotti/input/processados
# hdfs dfs -mkdir /user/vitorPazzotti/output/transferidos

wget --no-check-certificate --content-disposition git@github.com/vitor-pazzotti/Avalicao/archive/master.zip

unzip Avalicao-master.zip
rm -rf Avalicao-master.zip

mv Avalicao-master/CryptoCrawler.py vitorPazzotti/bin
mv Avalicao-master/dolar.py vitorPazzotti/bin
rm -rf Avalicao-master

##Crontab de execucao do arquivo Crypto  a cada 20 minutos
(crontab -l 2>/dev/null; echo "*/1 * * * * cd $PWD && /usr/bin/python3 $PWD/vitorPazzotti/bin/CryptoCrawler.py") | crontab -
#crontab executa dolar 1 vez por dia
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $PWD && /usr/bin/python3 $PWD/vitorPazzotti/bin/dolar.py") | crontab -
#Crontab consolida os arquivos crypto uma ver por dia todos os dia as 22:50
(crontab -l 2>/dev/null; echo "15 9 * * * cp $PWD/vitorPazzotti/crawler_crypto/*.csv $PWD/vitorPazzotti/crawler_crypto/consolidados") | crontab -
#Etapa de zipagem do crypto todo dia as 23:55
(crontab -l 2>/dev/null; echo "20 9 * * * cd $PWD/vitorPazzotti/crawler_crypto && zip processados.zip *.csv && mv processados.zip $PWD/vitorPazzotti/crawler_crypto/processados") | crontab -
#zipagem dolar
(crontab -l 2>/dev/null; echo "25 9 * * * cd $PWD/vitorPazzotti/crawler_dolar && zip processados.zip *.csv && mv processados.zip $PWD/vitorPazzotti/crawler_dolar/transferidos") | crontab -
#Joga arquivo no hdfs tanto do dolar quanto do crypto
# (crontab -l 2>/dev/null; echo "00 23 * * * cd $PWD/vitorPazzotti/crawler_crypto && hdfs dfs -put $PWD/vitorPazzotti/crawler_crypto/*.csv /user/vitorPazzotti/input") | crontab -
# (crontab -l 2>/dev/null; echo "00 23 * * * cd $PWD/vitorPazzotti/crawler_dolar && hdfs dfs -put $PWD/vitorPazzotti/crawler_dolar/*.csv /user/vitorPazzotti/input") | crontab -
#Envia programa .scala para o hdfs
# (crontab -l 2>/dev/null; echo "00 23 * * * cd $PWD/vitorPazzotti/bin && hdfs dfs -put $PWD/vitorPazzotti/bin/transforma.escala /user/vitorPazzotti/input") | crontab -
#Executa programa python para criação do Json, uma vez que o Scala nao funciona
(crontab -l 2>/dev/null; echo "30 9 * * * cd $PWD && /usr/bin/python3 $PWD/vitorPazzotti/conversao.py") | crontab -
#Apaga arquivos csv antigos para que o conversao.py rode todo dia pegando os arquivos certos
(crontab -l 2>/dev/null; echo "32 9 * * * cd PWD/vitorPazzotti/crawler_crypto/consolidados && rm -rf $PWD/vitorPazzotti/crawler_crypto/consolidados/*.csv") | crontab -
(crontab -l 2>/dev/null; echo "33 9 * * * cd $PWD/vitorPazzotti/crawler_dolar && rm -rf $PWD/vitorPazzotti/crawler_dolar/*.csv") | crontab -

