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
