# Teste de Carga

## Condições

* Considerar o início de um dia de aulas, às 9h.
* Iniciam-se 40 aulas ao mesmo tempo

**Dinâmica da Aula:**

1. O professor tem 10 minutos para criar a folha de registo 
2. Após o professor criar a folha de presencas, os 50 alunos presentes vao se registar ao longo de 5 minutos.
3. Durante estes mesmos 5 minutos, existe 50% de probabilidade do professor ter que registar manualmente alguns alunos (10 alunos neste caso)
4. Durante estes 5 minutos, o professor esteve continuamente a fazer refresh da folha de presenças.
5. No final dos 5 minutos, existe 25% de probabilidade do professor reparar que há alunos que se inscreveram, mesmo não estando na aula. Assim, este vai eliminar 10% dos alunos inscritos.
6. Posteriormente, o professor irá fechar o registo de presenças.

**No final da aula:**

1. O professor irá consultar a aula. Assim vai a consultar e escolhe a cadeira que esteve a lecionar
2. Depois disto, o professor escolhe o horário que quer consultar e carrega os dados da aula
3. Durante 2 minutos, o professor revê a listagem de alunos, fazendo continuamente refresh da tabela de presenças 



## Como Correr

Antes de mais, é necessário instalar o [Locust](https://locust.io/):
`python3 -m pip install locust`.

A versão atual do *locust* tem o problema de não permitir que acedamos ao número de clientes lançados, no código de python associado ao *lifecycle* dos mesmos. 

Devido a isto, se quisermos gerar um *lifecycle* finito, é necessário definirmos uma variável que guarde o número de clientes lançados, bem como o número de clientes que já terminaram o seu ciclo de vida.

Para tal, pode utilizar-se uma variável de ambiente!



**Registar Users:**

Antes de corrermos os testes de carga, é necessário criar utilizadores na BD. Para tal, vamos recorrer ao script `register_users.py`. A informação gerada vai ser guardada no ficheiro `user_data.tsv`, que depois será consumido durante o lifecylce do teste de carga. Devemos, então, remover este ficheiro antees de gerarmos novos users.

Assim, executamos:

```bash
rm user_data.tsv
export num_users_register=10
locust -f register_users.py -u $num_users_register -r 5 --host https://www.api-registo-presencas.aettua.pt --headless
```


**Testes de Carga:**

Podemos proceder agora aos testes de carga.

O ficheiro `lifecycle.py` contém todo o ciclo de vida de uma aula, definido na secção *Condições*. Assim, cada cliente lançado corresponde a uma aula a decorrer.


Assim, executamos:

```bash
export num_users_register=10
locust -f lifecycle.py -u $num_users_register --host https://www.api-registo-presencas.aettua.pt
```

Posteriormente vamos a `http://localhost:8090` e definimos a hatch rate.

A partir da interface web do *locust* conseguimos acompanhar todo o processo do teste de carga. No final, podemos fazer export dos reesultados para um `.csv`e analisar com mais detalhe. Enquanto o teste está a correr, convém ir checkando o terminal a partir do qual lançámos o testes, para ver se não rebentou nada.