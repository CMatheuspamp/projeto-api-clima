import requests
import sys
from datetime import datetime
import locale  # NOVO: Importamos a biblioteca de localização

# 1. OS NOSSOS DOIS ENDPOINTS DE API (SEGUROS E ABERTOS)
GEO_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# 2. ALTERAÇÃO: O dicionário de códigos de clima traduzido para PT-PT
CODIGOS_CLIMA = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Céu encoberto",  # Em vez de "Nublado"
    45: "Nevoeiro",
    51: "Chuvisco leve",  # Em vez de "Garoa"
    61: "Chuva fraca",  # Em vez de "Chuva leve"
    63: "Chuva moderada",
    65: "Chuva forte",
    80: "Aguaceiros fracos",  # Em vez de "leves"
    81: "Aguaceiros moderados",
    82: "Aguaceiros fortes",  # Em vez de "violentos"
    95: "Trovoada"
}


def buscar_coordenadas(cidade):
    """
    Etapa 1: Transforma o nome da cidade em coordenadas (Lat, Lon).
    """
    print(f"\nA geocodificar '{cidade}'...")
    try:
        # Prepara os parâmetros para a API de geocodificação
        params = {
            "name": cidade,
            "count": 1,  # Queremos apenas 1 resultado
            "language": "pt"
        }
        resposta = requests.get(GEO_API_URL, params=params)
        resposta.raise_for_status()  # Verifica erros (404, 500)

        dados = resposta.json()

        if not dados.get("results"):
            print(f"Erro: Cidade '{cidade}' não encontrada pela API de geocodificação.")
            return None

        resultado_cidade = dados["results"][0]

        return {
            "nome": resultado_cidade.get("name"),
            "pais": resultado_cidade.get("country"),
            "lat": resultado_cidade.get("latitude"),
            "lon": resultado_cidade.get("longitude"),
            "timezone": resultado_cidade.get("timezone")
        }

    except requests.exceptions.HTTPError as e:
        print(f"Erro de HTTP na geocodificação: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado na geocodificação: {e}")
        return None


def buscar_clima_api(coords):
    """
    Etapa 2: Usa as coordenadas para buscar a previsão do tempo.
    """
    print(f"A buscar clima para {coords['nome']}, {coords['pais']}...")
    try:
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "timezone": coords["timezone"],
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",  # O que queremos por dia
            "forecast_days": 4  # Hoje + 3 dias
        }

        resposta = requests.get(WEATHER_API_URL, params=params)
        resposta.raise_for_status()

        dados = resposta.json()

        print("\n--- PREVISÃO 4 DIAS (Open-Meteo) ---")

        lista_datas = dados["daily"]["time"]
        lista_codigos = dados["daily"]["weathercode"]
        lista_max_temps = dados["daily"]["temperature_2m_max"]
        lista_min_temps = dados["daily"]["temperature_2m_min"]

        for i in range(len(lista_datas)):
            data_obj = datetime.fromisoformat(lista_datas[i])

            # A formatação "%a" agora usará o locale pt_PT
            # (Ex: "Sex, 24/10")
            data_formatada = data_obj.strftime("%a, %d/%m")

            condicao = CODIGOS_CLIMA.get(lista_codigos[i], "Condição desconhecida")

            temp_max = lista_max_temps[i]
            temp_min = lista_min_temps[i]

            dia_str = "(Hoje)" if i == 0 else ""

            print(f"\n> {data_formatada} {dia_str}")
            print(f"  Condição: {condicao}")
            print(f"  Máx: {temp_max}°C | Mín: {temp_min}°C")

    except requests.exceptions.HTTPError as e:
        print(f"Erro de HTTP na busca de clima: {e}")
    except Exception as e:
        print(f"Erro inesperado na busca de clima: {e}")


if __name__ == "__main__":

    # 3. ALTERAÇÃO: Define o idioma (locale) para formatação de data
    # Isto irá "forçar" o %a a ser "Sex" em vez de "Fri"
    try:
        # Padrão para macOS/Linux
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    except locale.Error:
        try:
            # Padrão para Windows
            locale.setlocale(locale.LC_TIME, 'Portuguese_Portugal.1252')
        except locale.Error:
            # Se falhar, avisa o usuário e continua
            print("Aviso: Não foi possível definir o idioma para pt_PT. Dias da semana podem aparecer em inglês.")
            pass

    print("--- ☀️  Buscador de Clima (via API) ---")

    cidade_input = input("Digite o nome da cidade (ex: Lisboa, Porto, São Paulo): ").strip()

    if not cidade_input:
        print("A cidade não pode estar vazia. A sair.")
        sys.exit()

    coordenadas = buscar_coordenadas(cidade_input)

    if coordenadas:
        buscar_clima_api(coordenadas)

    print("\nBusca concluída.")