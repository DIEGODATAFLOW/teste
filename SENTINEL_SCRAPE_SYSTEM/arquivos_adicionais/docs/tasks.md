# Documentação Didática: Tarefas de Scraping com Celery

## Introdução

Este documento explica detalhadamente o código de uma tarefa de scraping assíncrona usando Celery. Vamos abordar cada parte do código para que você, como desenvolvedor júnior, possa entender completamente como tudo funciona.

## 1. Importações

```python
from celery import Celery
from app.config import settings
from app.webdriver.setup import get_chrome_driver
from selenium.webdriver.common.by import By
import time
```

### Explicação:

1. **Celery**: Framework para criação de tarefas assíncronas e filas de mensagens.
2. **settings**: Módulo de configuração da aplicação (deve conter URLs do broker e backend).
3. **get_chrome_driver**: Função personalizada para configurar o WebDriver do Chrome.
4. **By**: Do Selenium, para selecionar elementos na página (não usado diretamente aqui, mas útil para scraping).
5. **time**: Para pausas na execução (simulando trabalho ou esperando carregamento).

## 2. Configuração do Celery

```python
celery_app = Celery(
    "scraping_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
```

### Explicação:

Criamos uma instância do Celery com:
- `"scraping_tasks"`: Nome da aplicação Celery
- `broker`: URL do broker de mensagens (ex: Redis, RabbitMQ)
- `backend`: URL para armazenar resultados das tarefas

### Conceitos importantes:
- **Broker**: Sistema que gerencia a fila de mensagens/tarefas
- **Backend**: Armazena os resultados das tarefas para consulta posterior

## 3. Definição da Tarefa

```python
@celery_app.task(bind=True, name="execute_scraping")
def execute_scraping(self, request_data):
```

### Explicação:
- `@celery_app.task`: Decorador que transforma a função em uma tarefa Celery
- `bind=True`: Permite acessar o contexto da tarefa (self)
- `name="execute_scraping"`: Nome único para identificar a tarefa

## 4. Corpo da Tarefa

### 4.1 Atualização de Estado

```python
self.update_state(state="STARTED")
```

**O que faz?**:
- Atualiza o estado da tarefa para "STARTED"
- Útil para monitorar o progresso da tarefa

### 4.2 Configuração do WebDriver

```python
driver = get_chrome_driver(headless=True)
```

**O que faz?**:
- Cria uma instância do Chrome WebDriver em modo headless (sem interface gráfica)
- `headless=True` significa que o browser roda em background

### 4.3 Execução do Scraping

```python
driver.get(request_data["url"])
time.sleep(2)  # Simula trabalho
```

**O que faz?**:
- Acessa a URL fornecida em `request_data`
- `time.sleep(2)` pausa a execução por 2 segundos (simulando trabalho ou esperando carregamento)

### 4.4 Coleta de Resultados

```python
result = {
    "title": driver.title,
    "url": driver.current_url,
    "additional_data": request_data["parameters"],
}
```

**O que faz?**:
- Cria um dicionário com:
  - Título da página (`driver.title`)
  - URL atual (`driver.current_url`)
  - Quaisquer parâmetros adicionais passados em `request_data`

### 4.5 Encerramento do WebDriver

```python
driver.quit()
```

**Importante**:
- Sempre feche o WebDriver após o uso para liberar recursos

### 4.6 Retorno de Sucesso

```python
return {"status": "SUCCESS", "result": result, "error": None}
```

**Estrutura**:
- `status`: Indica sucesso
- `result`: Dados coletados
- `error`: None (sem erros)

## 5. Tratamento de Erros

```python
except Exception as e:
    if "driver" in locals():
        driver.quit()
    return {"status": "FAILURE", "result": None, "error": str(e)}
```

### Explicação:
- Captura qualquer exceção que ocorra
- Se o driver foi criado (`"driver" in locals()`), faz o cleanup
- Retorna um dicionário com:
  - `status`: "FAILURE"
  - `result`: None
  - `error`: Mensagem de erro convertida para string

## Fluxo Completo da Tarefa

1. Tarefa é criada e colocada na fila
2. Worker Celery pega a tarefa da fila
3. Atualiza estado para "STARTED"
4. Configura o WebDriver
5. Executa o scraping
6. Coleta resultados
7. Limpa recursos
8. Retorna resultado ou erro

## Como Usar Esta Tarefa

Para chamar a tarefa assincronamente:

```python
from seu_modulo import execute_scraping

task = execute_scraping.delay({
    "url": "https://exemplo.com",
    "parameters": {"param1": "valor1"}
})
```

Para monitorar o resultado:

```python
task.result  # Retorna o resultado quando pronto
task.status  # Mostra o estado atual
```

## Boas Práticas Implementadas

1. **Gerenciamento de recursos**: Sempre fecha o WebDriver, mesmo em caso de erro
2. **Tratamento de erros**: Captura exceções e retorna informações úteis
3. **Monitoramento**: Atualiza estados para acompanhamento
4. **Modularização**: Separa configuração (settings) da lógica

## Possíveis Melhorias

1. Adicionar timeouts para o scraping
2. Implementar retry para falhas temporárias
3. Adicionar mais estados intermediários
4. Logging detalhado

Esta documentação cobre todos os aspectos do código fornecido, explicando cada parte de forma didática para desenvolvedores juniores ou novos no Celery.