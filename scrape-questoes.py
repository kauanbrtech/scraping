import requests
from bs4 import BeautifulSoup
import sqlite3

def create_database():
    conn = sqlite3.connect('questoes_concursos.db')
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
    conn = sqlite3.connect('questoes_concursos.db')
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
        'Referer': 'https://www.qconcursos.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status da requisição: {response.status_code}")  # Verificar o status da requisição
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        questoes = []
        for questao in soup.find_all('div', class_='q-question-body'):  # Ajuste a classe conforme necessário
            print("Encontrou uma questão!")  # Verificar se está encontrando as questões
            try:
                # Enunciado da questão
                enunciado_elem = questao.find('div', class_='q-question-enunciation')
                enunciado = enunciado_elem.text.strip() if enunciado_elem else None
                
                # Alternativas da questão
                alternativas_elems = questao.find_all('label', class_='q-radio-button js-choose-alternative')
                alternativas = [alt.find('div', class_='q-item-enum js-alternative-content').text.strip() if alt.find('div', class_='q-item-enum js-alternative-content') else None for alt in alternativas_elems]
                
                # Resposta correta (se houver)
                resposta_correta_elem = questao.find('div', class_='js-response-correct')
                resposta_correta = resposta_correta_elem.find('span', class_='js-question-right-answer').text.strip() if resposta_correta_elem and resposta_correta_elem.find('span', class_='js-question-right-answer') else None
                
                # Explicação da resposta (se houver)
                explicacao_elem = questao.find('div', class_='q-answer-info-tip-content')
                explicacao = explicacao_elem.text.strip() if explicacao_elem else None
                
                # Informações adicionais da questão
                info = questao.find_previous_sibling('div', class_='q-question-info')
                ano_elem = info.find('span', String="Ano: ") if info else None
                ano = ano_elem.find("strong").next_sibling.strip() if ano_elem and ano_elem.next_sibling else None
                
                banca_elem = info.find('span', String="Banca: ",) if info else None
                banca = banca_elem.find('strong').text.strip() if banca_elem and banca_elem.find('strong') else None
                
                orgao_elem = info.find('span', String="Órgão: ") if info else None
                orgao = orgao_elem.find('strong').text.strip() if orgao_elem and orgao_elem.find('strong') else None
                
                prova_elem = info.find('span', class_="q-exams") if info else None
                prova = prova_elem.find('a').text.strip() if prova_elem and prova_elem.find('a') else None
                
                disciplina_elem = questao.find_previous_sibling('div', class_='q-question-mobile-info').find('span', class_='q-float-right') if questao.find_previous_sibling('div', class_='q-question-mobile-info') else None
                disciplina = disciplina_elem.text.strip() if disciplina_elem else None
                
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
    url = 'https://www.qconcursos.com/questoes-de-concursos/questoes'  # URL do site QConcursos
    questoes = get_questoes(url)
    if questoes:
        print(f"Foram encontradas {len(questoes)} questões.")
    else:
        print("Nenhuma questão encontrada.")

if __name__ == '__main__':
    main()
