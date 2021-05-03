# Workshop de Deployment - Parte 2

## 1. Before anything else...

Correr a aplicação em localhost e verificar se está tudo a funcionar corretamente.

Steps
``` bash
git clone https://github.com/AETT-UA/ws_deployment.git 
cd ws_deployment/base-part2/docker
docker-compose build
docker-compose up
```

Neste momento, para verificar se está tudo ok, devemos ir a http://127.0.0.1:8000 e:

1. Registar um novo utilizador
2. Fazer login com o novo user
3. Criar uma folha de presenças
4. Registar 1 ou 2 alunos
5. Consultar registos de presença
6. Fechar o registo de presenças
7. Logout
