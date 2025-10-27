import requests
import sys
from datetime import datetime
import locale  # Para garantir que as datas são formatadas em Português

# --- Configuração das APIs ---

# Endpoints (URLs) das APIs do Open-Meteo
GEO_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Dicionário de tradução para os códigos de clima (WMO weather codes) da API.
# Converte o código numérico (ex: 3) num texto amigável (ex: "Céu encoberto").
CODIGOS_CLIMA = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Céu encoberto",
    45: "Nevoeiro",
    51: "Chuvisco leve",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    80: "Aguaceiros fracos",
    81: "Aguaceiros moderados",
    82: "Aguaceiros fortes",
    95: "Trovoada"
}


def buscar_coordenadas(cidade):
    """
    Converte o nome de uma cidade (input) nas suas coordenadas.

    Usa a API de Geocodificação para encontrar a latitude, longitude e fuso horário,
    que são necessários para a API de clima.
    """
    print(f"\nA geocodificar '{cidade}'...")
    try:
        # Define os parâmetros para a chamada da API de Geocodificação
        params = {
            "name": cidade,  # O nome que o usuário digitou
            "count": 1,  # Queremos apenas 1 resultado (o mais provável)
            "language": "pt"  # Pedimos os resultados em português
        }

        # Faz o pedido GET para a API
        resposta = requests.get(GEO_API_URL, params=params)
        resposta.raise_for_status()  # Lança um erro se a resposta for 4xx ou 5xx (ex: 404, 500)

        # Converte a resposta (que é JSON) num dicionário Python
        dados = resposta.json()

        # Verifica se a API retornou algum resultado válido. Se não, 'results' estará vazio.
        if not dados.get("results"):
            print(f"Erro: Cidade '{cidade}' não encontrada pela API de geocodificação.")
            return None  # Retorna 'None' para sinalizar a falha ao fluxo principal

        # Se encontrou, pega o primeiro item (índice 0) da lista de resultados
        resultado_cidade = dados["results"][0]

        # Retorna um dicionário limpo com os dados que a próxima função (buscar_clima_api) precisa
        return {
            "nome": resultado_cidade.get("name"),
            "pais": resultado_cidade.get("country"),
            "lat": resultado_cidade.get("latitude"),
            "lon": resultado_cidade.get("longitude"),
            "timezone": resultado_cidade.get("timezone")
        }

    except requests.exceptions.HTTPError as e:
        # Tratamento de erro específico para falhas HTTP
        print(f"Erro de HTTP na geocodificação: {e}")
        return None
    except Exception as e:
        # Tratamento de erro genérico (ex: falha de rede)
        print(f"Erro inesperado na geocodificação: {e}")
        return None


def buscar_clima_api(coords):
    """
    Recebe o dicionário de coordenadas e busca a previsão do tempo.
    """
    print(f"A buscar clima para {coords['nome']}, {coords['pais']}...")
    try:
        # Prepara os parâmetros para a API de Clima
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "timezone": coords["timezone"],
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",  # Os dados diários que queremos
            "forecast_days": 4  # Hoje + 3 dias
        }

        # Faz o segundo pedido GET, desta vez para a API de clima
        resposta = requests.get(WEATHER_API_URL, params=params)
        resposta.raise_for_status()  # Verifica se há erros

        dados = resposta.json()

        print("\n--- PREVISÃO 4 DIAS (Open-Meteo) ---")

        # Estrutura de dados da API: A API retorna "listas paralelas".
        # Ex: O item [0] da lista_datas corresponde ao item [0] da lista_codigos.
        lista_datas = dados["daily"]["time"]
        lista_codigos = dados["daily"]["weathercode"]
        lista_max_temps = dados["daily"]["temperature_2m_max"]
        lista_min_temps = dados["daily"]["temperature_2m_min"]

        # Iteramos sobre os índices das listas (0, 1, 2, 3) para "juntar" os dados
        for i in range(len(lista_datas)):
            # Converte a data da API (string ISO, ex: "2025-10-27") num objeto datetime
            data_obj = datetime.fromisoformat(lista_datas[i])

            # Formata a data para "Seg, 27/10" (usando o 'locale' PT-PT definido abaixo)
            data_formatada = data_obj.strftime("%a, %d/%m")

            # Traduz o código de clima (ex: 3) para o texto (ex: "Céu encoberto")
            # .get() é usado para evitar erros; se o código não estiver no dicionário, retorna o texto padrão.
            condicao = CODIGOS_CLIMA.get(lista_codigos[i], "Condição desconhecida")

            # Pega nas temperaturas correspondentes
            temp_max = lista_max_temps[i]
            temp_min = lista_min_temps[i]

            # Adiciona a tag "(Hoje)" apenas ao primeiro dia (índice 0)
            dia_str = "(Hoje)" if i == 0 else ""

            # Imprime os resultados formatados
            print(f"\n> {data_formatada} {dia_str}")
            print(f"  Condição: {condicao}")
            print(f"  Máx: {temp_max}°C | Mín: {temp_min}°C")

    except requests.exceptions.HTTPError as e:
        print(f"Erro de HTTP na busca de clima: {e}")
    except Exception as e:
        print(f"Erro inesperado na busca de clima: {e}")



if __name__ == "__main__":

    # Define o "locale" (idioma) do script para Português de Portugal.
    # Isto é essencial para que o 'strftime("%a")' imprima "Seg" em vez de "Mon" (Monday).
    try:
        # Padrão para macOS/Linux
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    except locale.Error:
        try:
            # Padrão para Windows (em caso de o primeiro falhar)
            locale.setlocale(locale.LC_TIME, 'Portuguese_Portugal.1252')
        except locale.Error:
            # Se ambos falharem, avisa o usuário e continua (datas podem ficar em inglês)
            print("Aviso: Não foi possível definir o idioma para pt_PT. Dias da semana podem aparecer em inglês.")
            pass

    print("--- ☀️  Buscador de Clima (via API) ---")

    # Pede o input ao usuário e .strip() remove espaços em branco inúteis
    cidade_input = input("Digite o nome da cidade (ex: Lisboa, Porto, São Paulo): ").strip()

    # Validação simples para garantir que o usuário não deu só "Enter"
    if not cidade_input:
        print("A cidade não pode estar vazia. A sair.")
        sys.exit()  # Para o script

    # --- Fluxo Principal (2 Etapas) ---

    # Etapa 1: Obter as coordenadas
    coordenadas = buscar_coordenadas(cidade_input)

    # Etapa 2: Se a Etapa 1 for bem-sucedida (não retornou 'None'), buscar o clima
    if coordenadas:
        buscar_clima_api(coordenadas)

    print("\nBusca concluída.")