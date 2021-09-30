import sqlite3

conexao=sqlite3.connect('banco.db')
#cursor seleciona alguma coisa
cursor=conexao.cursor()

#criamos um scripts
cria_tabela="CREATE TABLE IF NOT EXISTS hoteis (hotel_id text PRIMARY_KEY,nome text, cidade text, estrelas float, \
diaria float)"
cria_hotel= "INSERT INTO hoteis VALUES ('alpha', 'Alpha', 'Rio de Janeiro', 5,'250')"


cursor.execute(cria_tabela)
cursor.execute(cria_hotel)

conexao.commit()
#E depois de enviar a gente da um close
conexao.close()
