# api-agrocontrol

api para o projeto agro control.

Obs: Este projeto foi construído para ser usado com Docker. Se você não quiser usar Docker, será necessário alterar os parâmetros de conexão.

## Requisitos
[Python](https://www.python.org/) version 3.8+  
[PIP](https://pip.pypa.io/en/stable/installation/)    
[Docker](https://www.docker.com/) (optional)  
[Postgres](https://www.postgresql.org/) version 15.6+ (optional)  
[Mongo](https://www.mongodb.com/pt-br) version 6.0+ (optional)  

## Começando
Primeiro, certifique-se de ter todos os requisitos instalados, caso contrário, você pode encontrar alguns problemas. 
Agora configure e instale todas as bibliotecas necessárias para este projeto.
1. Clone este repositório 
2. Crie um ambiente virtual para o diretório deste projeto:```python -m venv venv``` (opcional)
3. Ative o ambiente virtual (opcional)
3.1 No Linux/Mac ```source venv/bin/activate```
3.2 No Windows ```venv\Scripts\activate```
4. Execute  ```pip install -r requirements.txt```

Ou, se você tiver o Docker instalado, basta executar ```docker compose -f docker-compose.yml up```, e nenhuma configuração será necessária.

Obs: Existem arquivos de inicialização de banco de dados para este projeto em /config, você pode usá-los para iniciar os bancos de dados

## Executando este projeto
Para executar este projeto localmente, faça no seu terminal: ```uvicorn app:app --host 0.0.0.0 --port 5000```
Para o modo de desenvolvimento, adicione ```--reload```

Obs: uvicorn é suportado apenas em distribuições Linux/Mac. Para executar no Windows, por favor use Docker.

## Documentation

Esta API possui duas documentações, localizadas nos endpoints ```/docs``` ou ```/redoc```
