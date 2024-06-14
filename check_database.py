import sqlite3

def check_database():
    conn = sqlite3.connect('questoes_concursos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questoes')
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(row)

if __name__ == '__main__':
    check_database()
