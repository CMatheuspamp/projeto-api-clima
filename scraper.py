import requests
from bs4 import BeautifulSoup
import sys
import re  # NOVO: Para limpar o nome do artista/música

# 1. TEMPLATE DA URL DO GENIUS
URL_TEMPLATE = "https://genius.com/{ARTISTA_MUSICA}-lyrics"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}


def formatar_para_url(texto):
    """
    Função auxiliar para formatar "The Kid Laroi" em "The-Kid-Laroi"
    e "OVER YOU" em "Over-You".
    """
    # 1. Coloca em "Title Case" (ex: "OVER YOU" -> "Over You")
    texto_formatado = texto.title()

    # 2. Remove caracteres especiais (pontuação, etc.)
    # Deixa apenas letras, números e espaços
    texto_limpo = re.sub(r"[^a-zA-Z0-9\s-]", "", texto_formatado)

    # 3. Substitui espaços por hífens
    texto_final = texto_limpo.replace(" ", "-")

    # 4. Remove hífens duplicados (caso haja)
    texto_final = re.sub(r"-+", "-", texto_final)

    return texto_final


def buscar_letra_genius(artista, musica):
    """
    Função principal que faz o scraping do Genius.
    """
    print(f"\nA buscar letra de '{musica}' por '{artista}' no Genius...")

    try:
        # 1. FORMATAR OS NOMES PARA A URL
        artista_formatado = formatar_para_url(artista)
        musica_formatada = formatar_para_url(musica)

        # 2. CONSTRUIR A URL FINAL
        path_url = f"{artista_formatado}-{musica_formatada}"
        url_final = URL_TEMPLATE.replace("{ARTISTA_MUSICA}", path_url)

        print(f"A aceder: {url_final}")

        # 3. FAZER O SCRAPE
        pagina = requests.get(url_final, headers=HEADERS)

        # O Genius dá erro 404 se a música não existir.
        # Esta linha vai apanhar esse erro.
        pagina.raise_for_status()

        soup = BeautifulSoup(pagina.content, "html.parser")

        # 4. EXTRAIR A LETRA

        # O Genius coloca a letra em divs com o atributo 'data-lyrics-container="true"'
        # Usamos [] para procurar por atributos
        divs_letra = soup.find_all("div", {"data-lyrics-container": "true"})

        if not divs_letra:
            print("Erro: Página encontrada, mas os contentores da letra não.")
            print("O Genius pode ter atualizado o seu HTML.")
            return

        letra_completa = []

        print("\n--- LETRA ---")

        # Normalmente, a letra está toda no primeiro container
        # Vamos iterar por todos, só por segurança
        for container in divs_letra:
            # Usamos .get_text(separator="\n") para preservar as quebras de linha
            letra = container.get_text(separator="\n")
            print(letra)

        print("-------------")


    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"\nErro 404: Música não encontrada!")
            print(f"Verifique se o nome do artista '{artista}' e da música '{musica}' estão corretos.")
            print(f"(URL tentada: {url_final})")
        else:
            print(f"Erro de HTTP: {e}")
            print("O Genius pode estar a bloquear o script (Erro 403) ou estar em baixo.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    print("--- 🎵 Buscador de Letras de Música (Genius.com) ---")

    # 1. Pedir os inputs
    artista_input = input("Digite o nome do Artista (ex: The Kid Laroi): ").strip()
    musica_input = input("Digite o nome da Música (ex: OVER YOU): ").strip()

    # 2. Validar
    if not artista_input or not musica_input:
        print("Artista e Música são obrigatórios. A sair.")
        sys.exit()

    # 3. Chamar a função
    buscar_letra_genius(artista_input, musica_input)