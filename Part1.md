# Workshop de Deployment - Parte 1

Descrição do serviço a ser deployed:
* Serviço de marcação de presenças em aulas;
* Interface HTML+JS+CSS 
* REST API em Django

## 1. Before anything else...

Correr a aplicação em localhost e verificar se está tudo a funcionar corretamente.

Steps
``` bash
git clone https://github.com/AETT-UA/ws_deployment.git 
cd ws_deployment/base
./stop_on_ports.sh 8000 9000
./run.sh --rest-port 9000 --interface-port 8000
```
Ao correr o script run.sh, irão ser criados venvs com todos os packages necessário para correr a interface e a API. Posteriormente irá ser usado um HTTP Simple Server para disponibilizar a interface e vai ser corrido o projeto Django.

Após isto, podemos interagir com o serviço.

A interface gráfica estará disponível em http://127.0.0.1:8000.
PS: Para não acrescentar entropia ao workshop, sugere-se que seja utilizado Firefox.

Neste momento, devemos:

1. Registar um novo utilizador
2. Fazer login com o novo user
3. Criar uma folha de presenças
4. Registar 1 ou 2 alunos
5. Consultar registos de presença
6. Fechar o registo de presenças
7. Logout

Podemos também ver a documentação da API em: http://127.0.0.1:9000/documentation/ 

## 2. Correr a API REST utilizando o Gunircorn

**What is Gunicorn?**

[Gunicorn](https://gunicorn.org/) 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. It's a pre-fork worker model. The Gunicorn server is broadly compatible with various web frameworks, simply implemented, light on server resources, and fairly speedy.

Steps:

### 2.1 Instalar o Gunicorn

 ``` bash
cd base/rest_api
source venv/bin/activate
python3 -m pip install gunicorn
``` 


### 2.2 Correr o projeto com o Gunicorn
		
``` bash
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug
```

### 2.3 Correr Gunicorn com opções adiconais

Opções adicionais:
```
--workers -> The number of worker processes for handling requests
--max-requests  ->    The maximum number of requests a worker will process before restarting. 
```
 Considerações:
 ```
#workers <= num_cpu_multithread * 2
```
Run:
``` bash
gunicorn --bind 0.0.0.0:9000 --workers=4 --max-requests=500 rest.wsgi:application --log-level debug
```

Após isto, devemos ter a API disponível em http://127.0.0.1:9000/

### 2.4 O que acontece com static files?

Podem ir a http://127.0.0.1:9000/documentation e verificar que já não têm a interface do swagger.
Isto acontece porque o Gunicorn apenas irá servvir conteúdo dinâmico e não ficheiros estáticos. Para servir este ficheiros estáticos teremos posteriormente que usar um NGINX.


## 3. Correr a API REST em Production Mode

### 3.1 DEBUG Mode vs PRODUCTION Mode

Quando corremos projeto Django em DEBUG Mode, temos acesso a todos os logs de erros. Isto, em durante a fase de desenvolvimento, é bastante útil, contudo, em produção não queremos que os utilizadores seja capazes de ver como está o nosso código e quais as operações que estamos a realizar. Em Production Mode, se existir algum erro, o utilizador apenas irá saber que exisitu um erro, mas não vai ter acesso ao StackTrace do mesmo. 

Quando corremos em modo DEBUG, o Django vai ser servido por um webserver python bastante simples. Este é meramente um servidor de teste, sendo que, por exemplo, só aguenta com 100 conexões em simultâneo. Para além disto, este webserver irá disponibilizar ficheiros estáticos, o que, em Production Mode, não acontecerá.

Ao alterarmos para production mode temos de ter em atenção, por exemplo, a:

* BD que vamos usar
* Allowed Host
* CORS WhiteList
* etc...

### 3.2 Correr em Prod.

Para corrermos o projeto em produção temos de, em settings.py, alterar o valor da variável DEBUG para false.
Contudo, podemos querer alterar algumas configurações com base no facto de estarmos em produção, ou não. Por exemplo, a base de dados utilizada.

Assim, sugere-se a criação de uma variável de ambiente que defina como pretendem correr o projeto.

``` python
# rest_api/rest/settings.py
RUNNING_MODE = os.environ.get("RUNNING_MODE", None)
PRODUCTION = RUNNING_MODE is  not  None  and RUNNING_MODE.lower() == 'production'
DEBUG = not PRODUCTION
```

Depois, podemos configurar o que pretendemos fazer em cada um dos modos:

``` python
# rest_api/rest/settings.py
if PRODUCTION:
	print("REST API running in production environment.")
	# Update configs as you wish
	ALLOWED_HOSTS = ['*']
	ORS_ALLOW_ALL_ORIGINS = True
	SECURE_SSL_REDIRECT = False
	# Database
	# ToDo
else:
	print("REST API running in development environment.")
	CORS_ALLOW_ALL_ORIGINS = True
	ALLOWED_HOSTS = ['*']
	SECURE_SSL_REDIRECT = False
	# Database
	DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
		}
	}
```

Para testar, executar os seguintes comandos:
``` bash
export RUNNING_MODE=production
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug
```

Reparem no que acontece quando vão a http://127.0.0.1:9000/ 


Vamos voltar a correr em DEBUG Mode:
``` bash
export RUNNING_MODE=debug
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug
```

Vão novamente a http://127.0.0.1:9000/ e vejam a diferença 🙂

## 4. Base de Dados de Produção

Para correr o projeto em produção vamos utilizar uma base de dados PostgreSQL.  Para tal, vamos lançar um container com a mesma, ao nível da VM que vos foi atribuída.

Para tal façam ssh para a vossa VM e executem os seguintes comandos:

``` bash
cd database
docker-compose up
```

Ao nível do Dajngo é necessário alterar a BD a ser utilizada:

``` python
if PRODUCTION:
	print("REST API running in production environment.")
	# Update configs as you wish
	ALLOWED_HOSTS = ['*']
	CORS_ALLOW_ALL_ORIGINS = True
	SECURE_SSL_REDIRECT = False
	
	# Database
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
			'NAME': 'postgres',
			'USER': 'postgres',
			'PASSWORD': 'postgres',
			'HOST': 'deti-engsoft-01.ua.pt', # change this
			'PORT': 5432,
		}
	}
```

Podem correr novamente o projeto com:
``` bash
export RUNNING_MODE=production
# just to be sure :)
./stop_on_ports.sh 8000 9000 
./run.sh --rest-port 9000 --interface-port 8000 
```


## 5. Imagens Docker

Vamos agora criar imagens docker de forma a empacotarmos a nossa aplicação.
PS: As imagens docker que iremos criar são MVPs, uma vez que o core deste workshop não é a utilização de Docker.

### 5.1 REST API

Temos de criar um Dockerfile, para contruir a imagem docker

``` bash
# na root
mkdir -p docker/api
```

Vamos agora criar o ficheiro `Dockerfile`, com o conteúdo:

``` dockerfile
FROM python:3
COPY rest_api/ /app
ADD docker/api/entrypoint.sh /app
RUN  apt update -y
RUN apt install postgresql postgresql-contrib -y
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
```

No diretório `docker/api` vamos criar  o ficheiro `entrypoint.sh` com o conteúdo:

``` bash
#!/bin/bash
python3 manage.py makemigrations api
python3 manage.py migrate
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application --log-level debug
```

Podemos também iniciar já um docker-compose. Para tal, vamos criar o ficheiro `docker/docker-compose.yml`.

``` docker-compose
services:
	api:
		build:
			dockerfile: docker/api/Dockerfile
			context: ../
		ports:
		- 9000:9000
```

Neste momento podemos correr este docker compose (`docker-compose up`) e ir a http://127.0.0.1:9000 e verificar se a API está disponibilizada.

### 5.2 REST API - Extra

É bastante útil podermos realizar algumas configurações quando lançamos uma imagem docker. Ao nível da REST API, por exemplo, podemos utilizar variáveis de ambiente, que serão definidas quando corremos o docker container. Podemos aplicar isto, por exemplo, às configurações da base de dados de produção.

Para tal, temos de editar o ficheiro `rest_api/rest/settings.py`.

``` python
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': os.environ.get("DB_NAME", 'postgres'),
		'USER': os.environ.get("DB_USER", 'postgres'),
		'PASSWORD': os.environ.get("DB_PASSWORD", 'postgres'),
		'HOST': os.environ.get("DB_HOST", 'deti-engsoft-01.ua.pt'),
		'PORT': os.environ.get("DB_PORT", 5432),
	}
}
```

Temos agora que editar o nosso `docker-compose.yaml` de forma a definir estas variáveis de ambiente:

``` docker-compose
services:
	api:
		build:
			dockerfile: docker/api/Dockerfile
			context: ../
		ports:
			- 9000:9000
		environment:
			- RUNNING_MODE=production
			- DB_NAME=postgres
			- DB_USER=postgres
			- DB_PASSWORD=postgres
			- DB_HOST=deti-engsoft-01.ua.pt
			- DB_PORT=5432
```

### 5.3 Interface

Neste momento temos de servir a interface através de um webserver. Para tal vamos usar um NGINX.

Para tal, vamos alterar o nosso `docker-compose.yaml` para o seguinte:

``` docker-compose
services:
	nginx:
		image: nginx
		ports:
			- 8000:80
		volumes:
			- ../interface:/var/www/html/
			- ./interface/nginx.conf:/etc/nginx/nginx.conf
```

Posteriormente, temos de criar uma conf. para o NGINX. Criamos então o ficheiro `docker/interface/nginx.conf`com o seguinte conteúdo:

``` nginx
events {
  worker_connections  1024;
}
http {
    include mime.types;
    server {
        listen 80;

        location / {
            root /var/www/html/;
            index index.html;
        }
    }
}
```

### 5.4 Interface + REST API + DB

Neste momento, vamos ter de alterar os url mapping da interface.
Para tal, vamos criar um ficheiro `docker/interface/urls.js` e injetá-lo através do docker-compose.

``` docker-compose
services:
	nginx:
		image: nginx
		ports:
			- 8000:80
		volumes:
			- ../interface:/var/www/html/
			- ./interface/nginx.conf:/etc/nginx/nginx.conf
			- ./interface/urls.js:/var/www/html/static/js/urls.js
```

O `docker-compose.yaml` deve ficar assim:

``` docker-compose
services:
    api:
        build:
            dockerfile: docker/api/Dockerfile
            context: ../
        ports:
            - 9000:9000
        environment:
            - RUNNING_MODE=production
            - DB_NAME=postgres
            - DB_USER=postgres    
            - DB_PASSWORD=postgres
            - DB_HOST=deti-engsoft-01.ua.pt
            - DB_PORT=5432

    nginx:
        image: nginx
        ports:
            - 8000:80
        volumes:
            -  ../interface:/var/www/html/
            - ./interface/nginx.conf:/etc/nginx/nginx.conf
            - ./interface/urls.js:/var/www/html/static/js/urls.js
```


Depois devemos editar o ficheiro `docker/inteface/urls.js` para o seguinte:

``` js
// API URLs
let  base_api = "http://localhost:8000/api";
let  base_url = "http://localhost:8000";
```

Neste momento temos de editar a NGINX conf. para fazer um proxypass do endpoint `/api`para a REST API. Para tal vamos ter de mapear o docker service através do seu name (api) :

``` nginx
events {
  worker_connections  1024;
}
http {
    include mime.types;
    server {
        listen 80;

        location / {
            root /var/www/html/;
            index index.html;
        }

        location /api/ {
            proxy_pass http://api:9000/;
        }
    }
}
```

Neste momento podemos adicionar a BD ao `docker-compose`. Geralmente, é má política corrermos BDs em docker containers, contudo, para efeitos "educacionais" vamos fazê-lo.

Devemos, então acicionar um container com a BD e alterar a variavél `DB_HOST`da `api` para apontar para este container.
Podemos, também, adcionar as tags `dependends_on`.

O docker-compose deve ficar assim:
``` docker-compose
services:
    db:
        image: postgres
        ports:
            - 5432:5432
        volumes:
            - ./data/db:/var/lib/postgresql/data
        environment:
            - POSTGRES_DB=postgres
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=postgres

    api:
        build:
            dockerfile: docker/api/Dockerfile
            context: ../
        ports:
            - 9000:9000
        environment:
            - RUNNING_MODE=production
            - DB_NAME=postgres
            - DB_USER=postgres    
            - DB_PASSWORD=postgres
            - DB_HOST=db
            - DB_PORT=5432
        depends_on:
            - "db"

    nginx:
        image: nginx
        ports:
            - 8000:80
        volumes:
            -  ../interface:/var/www/html/
            - ./interface/nginx.conf:/etc/nginx/nginx.conf
            - ./interface/urls.js:/var/www/html/static/js/urls.js
        depends_on:
            - "api"
```

Contudo, vamos ter alguns problemas a resolver. Se a API se ligar primeiro que a BD, esta vai dar erro, uma vez que não consegue conectar-se à BD.

Para tal, vamos editar o entrypoint da API de forma a que esta espere pela BD 🙂.

Podemos instalar a cli do postgres ao nível no container da REST API. Para tal, vamos editar o ficheiro `docker/api/entrypoint.sh`para o seguinte:

``` dockerfile
FROM python:3
COPY . /app
RUN  apt update -y
RUN apt install postgresql postgresql-contrib -y
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN chmod +x rest_api_starter.sh
ENTRYPOINT ["./entrypoint.sh"]
```

Vamos então alterar o entrypoint (`docker/api/entrypoint.sh`) de forma a esperarmos pela BD:

```  bash
#!/bin/bash

RETRIES=40

until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES--)) remaining attempts..."
  sleep 5
done

echo "Connected to database!."

python3 manage.py makemigrations api
python3 manage.py migrate
gunicorn --bind 0.0.0.0:9000 rest.wsgi:application
--log-level debug
```

Após isto, podemos verificar se está tudo funcional:
``` bash
cd docker 
docker-compose build
docker-compose up
```


## 6. Caching

Vamos configurar os mecanismos de caching ao nível do NGINX. 
Neste caso, os nossos recursos vão ficar em cache durante 5 dias.

``` nginx
# cache
expires 5d;
add_header Cache-Control "public, no-transform";
```

De forma a reduzirmos a largura de banda utilizada, podemos também servir os recursos de forma comprimida. Para tal, utilizaremos indicativas do gzip.

``` nginx
gzip on;
gzip_static on;
gzip_disable "msie6";
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_buffers 16 8k;
gzip_http_version 1.1;
```

Temos de ter cuidado, contudo, uma vez que os algoritmos de compressão consomem CPU, quer do lado do servidor, quer do lado do cliente, que irá ter de fazer decompress dos ficheiros. Assim, temos de definir um nível de compressão através de variáveis como `gzip_min_length`, `gzip_comp_level`, etc...

Podemos, então, altarar a nossa config NGINX para:

``` nginx
events {
  worker_connections  1024;
}
http {
    include mime.types;
    server {
        listen 80;

        location / {
            root /var/www/html/;
            index index.html;
            
            # gzip  
            gzip on;
            gzip_static on;
            gzip_disable "msie6";
            gzip_vary on;
            gzip_proxied any;
            gzip_comp_level 6;
            gzip_buffers 16 8k;
            gzip_http_version 1.1;
            gzip_types application/javascript application/rss+xml application/vnd.ms-fontobject application/x-font application/x-font-opentype application/x-font-otf application/x-font-truetype application/x-font-ttf application/x-javascript application/xhtml+xml application/xml font/opentype font/otf font/ttf image/svg+xml image/x-icon text/css text/javascript text/plain text/xml;
            
            # cache
            expires 5d;
            add_header Cache-Control "public, no-transform";        
        }

        location /api/ {
            proxy_pass http://api:9000/;
        }
    }
}
```

Após isto, podemos verificar se está tudo funcional:
``` bash
docker-compose down
docker-compose down
```

A primeira vez que abrirem o nosso site, deve encontrar-se com uma network semelhante a esta:

![No cache](https://i.imgur.com/Vo6WwGG.png)

Contudo, na segunda vez que consultarem o site, os ficheiros já devem estar a ser servidos a partir da cache:

![With cache](https://imgur.com/s7dvYm6.png)


Também podemos ver que os ficheiros foram zipados:

![gzip](https://imgur.com/0b9vEog.png)



## 7. Escalabilidade e Load Balancing

Se contruirmos uma REST API stateless, podemos facilmente replicá-la de forma a aumentarmos a quantidade de clientes suportados pelo sistema. Neste workshop vamos simular a escalabilidade da REST API através do deployment de 2 instâncias da REST API.
Posteriormente, vamos utilizar o NGINX para distribuir a carga entre estas 2 réplicas. Isto tem apenas um propósito educacional, uma vez que há melhores formas de fazer auto-scaling da nossa aplicação. Contudo, uma vez que estamos limitados pela duração do workshop, esta é uma boa forma de explorarmos o load balancing do NGINX.

Desta forma, vamos editar o nosso docker-compose para o seguinte:

``` docker-compose
services:
    db:
        image: postgres
        ports:
            - 5432:5432
        volumes:
            - ./data/db:/var/lib/postgresql/data
        environment:
            - POSTGRES_DB=postgres
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=postgres

    api_1:
        build:
            dockerfile: docker/api/Dockerfile
            context: ../
        environment:
            - RUNNING_MODE=production
            - DB_NAME=postgres
            - DB_USER=postgres    
            - DB_PASSWORD=postgres
            - DB_HOST=db
            - DB_PORT=5432
        depends_on:
            - "db"
    
    api_2:
        build:
            dockerfile: docker/api/Dockerfile
            context: ../
        environment:
            - RUNNING_MODE=production
            - DB_NAME=postgres
            - DB_USER=postgres    
            - DB_PASSWORD=postgres
            - DB_HOST=db
            - DB_PORT=5432
        depends_on:
            - "db"


    nginx:
        image: nginx
        ports:
            - 8000:80
        volumes:
            -  ../interface:/var/www/html/
            - ./interface/nginx.conf:/etc/nginx/nginx.conf
            - ./interface/urls.js:/var/www/html/static/js/urls.js
        depends_on:
            - "api_1"
            - "api_2"
```

Vamos também, ter que configurar o nosso NGINX para fazer load balancing:

``` nginx
events {
  worker_connections  1024;
}
http {
    upstream api {
        server api_1:9000;
        server api_2:9000;
    }

    include mime.types;
    server {
        listen 80;

        location / {
            root /var/www/html/;
            index index.html;

            # gzip  
            gzip on;
            gzip_static on;
            gzip_disable "msie6";
            gzip_vary on;
            gzip_proxied any;
            gzip_comp_level 6;
            gzip_buffers 16 8k;
            gzip_http_version 1.1;
            gzip_types application/javascript application/rss+xml application/vnd.ms-fontobject application/x-font application/x-font-opentype application/x-font-otf application/x-font-truetype application/x-font-ttf application/x-javascript application/xhtml+xml application/xml font/opentype font/otf font/ttf image/svg+xml image/x-icon text/css text/javascript text/plain text/xml;
            
            # cache
            expires 5d;
            add_header Cache-Control "public, no-transform";
        }

        location /api/ {
            proxy_pass http://api/;
        }
    }
}```


Para verificarmos que existe um balancemanto de carga devemos registar um novo utilizador e realizar algumas operações.

Depois:

``` bash
docker ps
docker logs <id_container_api_1>
docker logs <id_container_api_2>
``` 

Devemos ver os seguintes logs:

![gzip](https://imgur.com/QstTWK9.png)


