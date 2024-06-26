import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import sqlite3

def create_database():
    conn = sqlite3.connect('questoes_tecconcursos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enunciado TEXT,
        alternativas TEXT,
        resposta_correta TEXT,
        explicacao TEXT,
        ano TEXT,
        banca TEXT,
        orgao TEXT,
        prova TEXT,
        disciplina TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect('questoes_tecconcursos.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO questoes (enunciado, alternativas, resposta_correta, explicacao, ano, banca, orgao, prova, disciplina)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def get_questoes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.tecconcursos.com.br/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status da requisição: {response.status_code}")  # Verificar o status da requisição
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        questoes = []
        for questao in soup.find_all('div', class_='questao-item'):  # Ajuste a classe conforme necessário
            print("Encontrou uma questão!")  # Verificar se está encontrando as questões
            try:
                # Enunciado da questão
                enunciado_elem = questao.find('div', class_='questao-conteudo').find('a')
                enunciado = enunciado_elem.text.strip() if enunciado_elem else None
                
                # Informações adicionais da questão
                header = questao.find('div', class_='questao-header')
                
                questao_id_elem = header.find('div', class_='questao-id')
                questao_id = questao_id_elem.text.strip() if questao_id_elem else None
                
                banca_elem = header.find('a', title="Informações da banca")
                banca = banca_elem.text.strip() if banca_elem else None
                
                prova_elem = header.find('a', title="Informações deste concurso")
                prova = prova_elem.text.strip() if prova_elem else None
                
                orgao_elem = header.find('a', title="Informações do Órgão")
                orgao = orgao_elem.text.strip() if orgao_elem else None
                
                disciplina_elem = header.find('a', title="Informações da matéria")
                disciplina = disciplina_elem.text.strip() if disciplina_elem else None
                
                ano_elem = header.find('div', class_='questao-header').find('a', title="Informações deste concurso")
                ano = ano_elem.text.split('/')[-1] if ano_elem else None

                # Alternativas da questão
                alternativas_elems = questao.find_all('label', class_='questao-enunciado-alternativa')
                alternativas = [alt.find('div', class_='questao-enunciado-alternativa-texto').text.strip() for alt in alternativas_elems]
                
                # Resposta correta (se houver)
                resposta_correta = None
                for alt in alternativas_elems:
                    input_elem = alt.find('input', {'disabled': False})
                    if input_elem:
                        resposta_correta = alt.find('div', class_='questao-enunciado-alternativa-texto').text.strip()
                        break

                explicacao = None  # Não há explicação visível diretamente na página inicial
                
                questao_data = (enunciado, ', '.join(alternativas) if alternativas else None, resposta_correta, explicacao, ano, banca, orgao, prova, disciplina)
                questoes.append(questao_data)
                
                # Imprime a questão para verificação
                print(f"Enunciado: {enunciado}")
                print(f"Alternativas: {alternativas}")
                print(f"Resposta Correta: {resposta_correta}")
                print(f"Explicação: {explicacao}")
                print(f"Ano: {ano}")
                print(f"Banca: {banca}")
                print(f"Órgão: {orgao}")
                print(f"Prova: {prova}")
                print(f"Disciplina: {disciplina}")
                print("-" * 50)
                
                # Inserir no banco de dados
                insert_data(questao_data)
            except Exception as e:
                print(f"Erro ao processar questão: {e}")
        
        return questoes
    else:
        print("Não foi possível obter as questões.")
        return []

def main():
    create_database()
    url = 'https://www.tecconcursos.com.br/questoes/'  # URL do site TecConcursos
    questoes = get_questoes(url)
    if questoes:
        print(f"Foram encontradas {len(questoes)} questões.")
    else:
        print("Nenhuma questão encontrada.")

if __name__ == '__main__':
    main()
