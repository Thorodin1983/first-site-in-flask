# conexao.py
import pyodbc

def create_connection():
    try:
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                              'Server=SERVDB4\\SQLEXPRESS;'
                              'Database=RA;'
                              'UID=sa;'
                              'PWD=Luan@1983;')
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print("Erro ao conectar:", e)
        return None
