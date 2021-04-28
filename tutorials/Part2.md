
## 7. Monitoring de métricas

Para fazermos o monitoring de métricas vamos usar a TICK Stack:
* Telegraf
* InfluxDB
* Chronograph
* Kapacitor

As VMs já têm instalada esta stack sendo que os diversos componentes estão disponíveis em:

* InfluxDB - porta 8086
* Chronograph - porta 8088

### 7.1 Criação de uma BD, ao nível da InfluxDB

1. SSH para a máquina
2. `influx -precision rfc3339`
3. `CREATE DATABASE telegraf`
4. `exit`

### 7.2 Configuração do Chronograph

1. Aceder, num browser,  a `<vm_ip>:8888` (exemplo: http://deti-engsoft-01.ua.pt:8888/) 
2. Configurar os parâmetros:
* Connection url: [http://localhost:8086](http://localhost:8086)
* Connection name: Influx DB
* Username: user
* Password: password
* Telegraf Database: telegraf

3. Por agora, vamos apenas escolher o dashboard de system
4. Dar skip na connfiguração do kapacitor 

### 7.3 Correr o Telegraf para o envio de métricas

O telegraf disponibiliza diversas plugins para recolher métricas:

* nginx;
* redis;
* postgresql;
* haproxy;
* cpu;
* system;
* mem;
* disk;
* network;
* ...

Portanto, será necessário escolhermos quais os plugins que vamos usar dentro de cada container. Podemos utilizar os seguintes:

| Container | Listagem plugins |
| --- | --- |
| All | cpu, system, mem, disk, network |
| db | postgresql |
| nginx | nginx |
  
Criem o diretório `docker/tools` e façam o download do binário do telegraf.

1. `wget https://github.com/AETT-UA/ws_deployment/raw/main/tools/telegraf`
2. `sudo chmod +x telegraf`


Posteriormente, vamos ter de criar as diversas configurações do telegraf.

Entrar em `docker\api`e criar um `api_telegraf.conf` com a informação presente [aqui](https://github.com/AETT-UA/ws_deployment/blob/main/tools/telegraf/api_telegraf.conf).

Reparem que estamos a usar diversas variáveis de ambiente para configurar o telegraf:

``` bash
hostname = "$HOST"
urls = ["$INFLUX_DB_URL"]
database = "$INFLUX_DB_NAME"
```

Vamos, então dar set destas confs:

```bash
export HOST=test
export INFLUX_DB_URL=http://<localizacao da vossa maquina>:8086
export INFLUX_DB_NAME=telegraf
```

Podem testar a configuração através do comando:

`telegraf  -config ../api/api_telegraf.conf --test`
(correr dentro de `docker/tools`)

Se tudo correr bem, devem ver algumas métricas que estão a ser recolhidas.

Depois, podem correr o telegraf durante 1 ou 2 minutos e verificar se as métricas estão a ser display no chronograph.

`telegraf  -config ../api/api_telegraf.conf `


![telegraf](https://i.imgur.com/Ly9CA1J.png)


Neste momento estamos em conndições de alterar a imagem docker da API para correr o telegraf.

Nas variáveis de ambiente da API adicionar:

```docker-compose
# Telegraf
- INFLUX_DB_URL=http://deti-engsoft-01.ua.pt:8086
- INFLUX_DB_NAME=telegraf
- IMAGE_NAME=API
```

Agora, vamos ter de adicionar o binário do telegraf à imagem da API. Para tal, vamos editar o ficheiro `docker/api/Dockerfile`para o seguinte:

``` dockerfile
FROM python:3
COPY rest_api/ /app
ADD docker/api/entrypoint.sh /app
ADD docker/tools/telegraf /usr/bin/
ADD docker/api/api_telegraf.conf /app
RUN  apt update -y
RUN apt install postgresql postgresql-contrib -y
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x /usr/bin/telegraf
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
```

Vamos, também, ter que fazer algumas alterações ao `docker/api/entrypoint.sh`:

```bash
#!/bin/bash

RETRIES=40

until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 5
done

echo "Connected to database!."

# save ip in an environment variable
export HOST=$IMAGE_NAME-$(hostname) 
# Run metric collector - telegraf
eval "telegraf --config api_telegraf.conf &"

python3 manage.py makemigrations api
python3 manage.py migrate
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug
```

Vamos agora passar ao PostgreSQL.
Anteriormente estávamos a utilizar uma imagem default de postgtres, sendo que agora não será possível. Teremos, portanto, que alterar o `Dockerfile` e o `entrypoint.sh` da imagem original.

Para tal, primeiro, vamos fazer o download do `Dockerfile` e `entrypoint.sh` originais.

```bash
cd docker
mkdir postgresql
cd postgresql
wget https://raw.githubusercontent.com/docker-library/postgres/7bd41786539082857396f4d1b4f1cb326ebee8de/13/docker-entrypoint.sh
wget https://raw.githubusercontent.com/docker-library/postgres/7bd41786539082857396f4d1b4f1cb326ebee8de/13/Dockerfile
```

Vamos agora criar a configuração do telegraf. Entrar em `docker\postgresql`e criar um `postgresql_telegraf.conf` com a informação presente [aqui](https://github.com/AETT-UA/ws_deployment/blob/main/tools/telegraf/postgresql_telegraf.conf).


Posteriormente, vamos ter de fazer alterações a estes ficheiros.
Em `docker/postgresl/docker-entrypoint.sh`na função `main`, devemos acrescentar o seguinte código, após o segundo `if`:

```bash
# changed/new
# save ip in an environment variable
export HOST=$IMAGE_NAME-$(hostname)
# Run metric collector - telegraf
eval  "telegraf --config postgresql_telegraf.conf &"
# end changed/new 
```

Em `docker/postgresl/Docckerfile`, devemos alterar o código que está antes da definição do `entrypoint` para:

```Dockerfile
ADD docker/postgresql/docker-entrypoint.sh /
ADD docker/tools/telegraf /usr/bin/
ADD docker/postgresql/postgresql_telegraf.conf /
RUN chmod +x /usr/bin/telegraf
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
```

Também devemos editar o `docker-compose.yaml`:

```docker-compose

services:
    db:
        build:
            dockerfile: docker/postgresql/Dockerfile
            context: ../
        ports:
            - 5432:5432
        volumes:
            - ./data/db:/var/lib/postgresql/data
        environment:
            - POSTGRES_DB=postgres
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=postgres
            # Telegraf
            - INFLUX_DB_NAME=telegraf
            - IMAGE_NAME=DB
            - INFLUX_DB_URL=http://deti-engsoft-01.ua.pt:8086
...
...
...
```

Vamos ter de fazer o mesmo com a nossa imagem de nginx:

```bash
cd docker/interface
wget https://raw.githubusercontent.com/nginxinc/docker-nginx/464886ab21ebe4b036ceb36d7557bf491f6d9320/mainline/debian/Dockerfile
wget https://raw.githubusercontent.com/nginxinc/docker-nginx/464886ab21ebe4b036ceb36d7557bf491f6d9320/mainline/debian/docker-entrypoint.sh
wget https://raw.githubusercontent.com/nginxinc/docker-nginx/464886ab21ebe4b036ceb36d7557bf491f6d9320/mainline/debian/30-tune-worker-processes.sh
wget https://raw.githubusercontent.com/nginxinc/docker-nginx/464886ab21ebe4b036ceb36d7557bf491f6d9320/mainline/debian/10-listen-on-ipv6-by-default.sh
wget https://raw.githubusercontent.com/nginxinc/docker-nginx/464886ab21ebe4b036ceb36d7557bf491f6d9320/mainline/debian/20-envsubst-on-templates.sh
```


Vamos agora criar a configuração do telegraf. Entrar em `docker\interface`e criar um `nginx_telegraf.conf` com a informação presente [aqui](https://github.com/AETT-UA/ws_deployment/blob/main/tools/telegraf/nginx_telegraf.conf).


Posteriormente, vamos ter de fazer alterações a estes ficheiros.
No final de `docker/interface/docker-entrypoint.sh`, antes de `exec  "$@"`, devemos acrescentar o seguinte código:

```bash
# changed/new
# save ip in an environment variable
export HOST=$IMAGE_NAME-$(hostname)
# Run metric collector - telegraf
eval  "telegraf --config nginx_telegraf.conf &"
# end changed/new 
```

Em `docker/interface/Dockerfile`, devemos alterar o código que está antes da definição do `entrypoint` para:

```Dockerfile
# changed/new
COPY docker/interface/docker-entrypoint.sh /
COPY docker/interface/10-listen-on-ipv6-by-default.sh /docker-entrypoint.d
COPY docker/interface/20-envsubst-on-templates.sh /docker-entrypoint.d
COPY docker/interface/30-tune-worker-processes.sh /docker-entrypoint.d
ADD docker/tools/telegraf /usr/bin/
ADD docker/interface/nginx_telegraf.conf /
RUN chmod +x /usr/bin/telegraf
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
# end changed/new
```

Também devemos editar o `docker-compose.yaml`:

```docker-compose
services:
...
...
...
    nginx:
        build:
            dockerfile: docker/interface/Dockerfile
            context: ../
        ports:
            - 8000:80
        volumes:
            -  ../interface:/var/www/html/
            - ./interface/nginx.conf:/etc/nginx/nginx.conf
            - ./interface/urls.js:/var/www/html/static/js/urls.js
        environment:
            # Telegraf
            - INFLUX_DB_NAME=telegraf
            - IMAGE_NAME=NGINX
            - INFLUX_DB_URL=http://deti-engsoft-01.ua.pt:8086
        depends_on:
            - "api"
```

Também teremos de exportar algumas métricas, ao nível do NGINX. Estas serão disponibilizadas num end-point que só o localhost poderá aceder. Para tal, dentro da configuração `server`, na `nginx.conf`, adicionar:
``` nginx
location /nginx_status {
	 # Turn on nginx stats
	 stub_status on;
	 # I do not need logs for stats
	 access_log   off;
	 # Security: Only allow access from 192.168.1.100 IP 
	 allow 127.0.0.1;
	 # Send rest of the world to /dev/null 
	 deny all;
}
```


### 7.4 nova Configuração do Chronograph + Kapacitor

1. Aceder, num browser,  a `<vm_ip>:8888` (exemplo: http://deti-engsoft-01.ua.pt:8888/) 
2. Ir a configuration e escolher a BD que estamos a usar
3. Configurar os parâmetros:
* Connection url: [http://localhost:8086](http://localhost:8086)
* Connection name: Influx DB
* Username: user
* Password: password
* Telegraf Database: telegraf
4. Dar update da connection
5. Escolher os Dashboards:
* NGINX
* PostgreSQL
* System
6. Adicionar o kapacitor:
* Connection url: [http://localhost:9092](http://localhost:9092)
* Name: Kapacitor
7. Update/ Create


### 7.5 Visualizar Dashboards

Vamos a http://\<vm\>:8888/ e entramos na aba "Dashboards". Ver se estamos a obter métricas

### 7.6 Definir alarmes

Ir a Alerting > Manage Tasks > Build Alert Rule

* Alert Name: Max Mem
* Alert Type: threshold
* Time series:
	* telegraf.autogen
	* mem
	* used_percent
* Conditions:
	* used is greater than 35
* Alert Handler: Slack
* Agora temos de configurar o webhook do slack
	* Webhook URL: [https://hooks.slack.com/services/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](https://hooks.slack.com/services/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)
	* Channel: #alerts
	* Enable configuration: true
* Message: 
	* ` [Rafael Direito] {{.ID}} is  {{.Level}} -> value : {{ index .Fields "value" }}`

Agora podem criar mais alarmes, conforme acharem necessário.

Para verem os alertas, entrem em: ws-deployment-aettua.slack.com .

## 8. Correr toda a stack na VM

Vamos agora correr tudo na VM:

``` bash
# Em ws_deployment
rm -rf base-part2/docker/data 
scp -r base-part2 aettua@<vm_ip>:~/

# Entrar na VM
ssh aettua@<vm>

# Alterar os urls da rest api, ao nivel da interface
vim base-part2/docker/interface/urls.js
```

Os mappings devem ser os seguintes:

```js
let base_api = "http://<vm_ip>:8000/api";
let base_url = "http://<vm_ip>:8000";
```

Agora, vamos correr o docker-compose.

```bash 
cd base-part2/docker/
docker-compose build
docker-compose up
```

## 9. Testes de Carga

Primeiramente devemos definir um cenário de teste. Para depois implementar mecanismos de teste específicos para o mesmo.
Este cenario está definido em [aqui](https://github.com/AETT-UA/ws_deployment/blob/main/tools/testing/README.md).

Vamos analisá-lo.

```bash
cd tools/testing
python3 -m pip install -r requirements.txt

rm user_data.tsv
#definir numero de users a registar
export num_users_register=200
# registar users
locust -f register_users.py -u $num_users_register -r 5 --host http://<vm>:8000/api --headless
# testes de carga
locust -f lifecycle.py -u $num_users_register --host  http://<vm>:8000/api
```

Agora podemos ir a [http://127.0.0.1:8089](http://127.0.0.1:8089) e definir uma hatch rate de 7. Depois, começamos o teste de carga.

Agora podemos ver se o nosso sistema aguentou com esta carga. Vamos verificar se: 

* O tempo de resposta está demasiado elevado
* Se temos uma percentagem elevada de failures


### Notes

Quem tiver problemas em instalar o `psycopg2` em Mac, pode executar este comando `export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/`. This should do it.

Para limpar a InfluxDB:

``` bash
influx -precision rfc3339
> show databases
> use telegraf
> DROP SERIES FROM /.*/ 
```

