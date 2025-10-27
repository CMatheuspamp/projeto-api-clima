# ☀️ Buscador de Clima (via API)

Projeto de back-end em Python desenvolvido como parte de um portfólio de estágio.

Este é um script de console interativo que consome duas APIs abertas (Open-Meteo) para fornecer a previsão do tempo para os próximos 4 dias de qualquer cidade do mundo.

## 🎯 Funcionalidades

* **Geocodificação em 2 Etapas:** O usuário digita o nome de uma cidade (ex: "Porto").
* **Etapa 1:** O script consome a API de Geocodificação (`geocoding-api.open-meteo.com`) para transformar "Porto" em coordenadas (latitude e longitude).
* **Etapa 2:** O script consome a API de Clima (`api.open-meteo.com`) usando essas coordenadas.
* **Tratamento de Erros:** O script lida com cidades não encontradas e erros de API.
* **Localização PT-PT:** As datas (dias da semana) e as condições climáticas são formatadas para Português de Portugal.

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **`requests`**: Para fazer as chamadas HTTP às APIs.
* **`datetime`**: Para formatar e comparar as datas.
* **`locale`**: Para garantir a formatação de datas em PT-PT.

## 🚀 Como Executar

1.  Clone este repositório:
    ```bash
    git clone [https://www.youtube.com/watch?v=xtwls2XmJUI](https://www.youtube.com/watch?v=xtwls2XmJUI)
    cd projeto-api-clima
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip3 install -r requirements.txt
    ```

4.  Execute o script:
    ```bash
    python3 clima_app.py
    ```

5.  Siga as instruções no terminal!