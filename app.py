# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session

import conexao
from conexao import create_connection

app = Flask(__name__)
app.secret_key = 'Luan'  # Necessário para usar sessões


@app.route('/login')
def loga():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifique o nome de usuário e a senha no banco de dados
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username  # Armazena o nome de usuário na sessão
            return redirect(url_for('home'))
        else:
            return "Login inválido. Tente novamente."

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão ao fazer logout
    return redirect(url_for('login'))



@app.route('/home')
def home():
    username = session.get('username')  # Obtém o nome de usuário da sessão
    if not username:
        return redirect(url_for('login'))  # Se não estiver logado, redirecione para a página de login
    return render_template('home.html', username=username)


@app.route('/cadastrar_reclamacao', methods=['GET', 'POST'])
def cadastrar_reclamacao():
    if request.method == 'POST':
        data_reclamacao = request.form.get('data_reclamacao')

        # Validação: apenas a data da reclamação é obrigatória
        if not data_reclamacao:
            return "Erro: A data da reclamação é obrigatória."

        # Conexão com o banco de dados
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # Montando a consulta SQL de inserção
                cursor.execute("""
                    INSERT INTO reclamacoesRa (
                        data_reclamacao, nome, id_reclamacao, motivo_legenda_reclamacao, ocorrencia, produto,
                        nivel, replica, resposta_publica, avaliacao, nota,
                        voltaria_fazer_negocio, caso_resolvido, o_que_houve_no_atendimento,
                        moderacao_solicitada, data_moderacao, motivo_moderacao, moderacao_aceita,
                        motivo_negativa, segmento, responsavel
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_reclamacao,
                    request.form.get('nome', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('id_reclamacao', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('motivo_legenda_reclamacao', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('ocorrencia', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('produto', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('nivel', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('replica', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('resposta_publica', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('avaliacao', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('nota', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('voltaria_fazer_negocio', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('caso_resolvido', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('o_que_houve_no_atendimento', ''),
                    # Preencher com valor vazio se não for informado
                    request.form.get('moderacao_solicitada', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('data_moderacao', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('motivo_moderacao', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('moderacao_aceita', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('motivo_negativa', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('segmento', ''),  # Preencher com valor vazio se não for informado
                    request.form.get('responsavel', '')  # Preencher com valor vazio se não for informado
                ))

                conn.commit()
                return redirect(url_for('home'))
            except Exception as e:
                print("Erro ao cadastrar a reclamação:", e)
            finally:
                cursor.close()
                conn.close()
        return "Erro na conexão com o banco de dados."

    return render_template('home.html')


@app.route('/buscar_reclamacoes', methods=['GET'])
def buscar_reclamacoes():
    # Conecta ao banco de dados
    conn = create_connection()
    reclamacoes = []

    if conn:
        try:
            cursor = conn.cursor()
            # Query básica para buscar todas as reclamações
            query = "SELECT id_reclamacao, nome, data_reclamacao, segmento, produto FROM reclamacoesRa WHERE 1=1"

            # Adiciona filtros com base nos parâmetros fornecidos no formulário
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            id_reclamacao = request.args.get('id_reclamacao')
            atendimento = request.args.get('segmento')
            nome = request.args.get('nome')

            # Condições dinâmicas
            params = []
            if data_inicio:
                query += " AND data_reclamacao >= ?"
                params.append(data_inicio)
            if data_fim:
                query += " AND data_reclamacao <= ?"
                params.append(data_fim)
            if id_reclamacao:
                query += " AND id_reclamacao = ?"
                params.append(id_reclamacao)
            if atendimento:
                query += " AND atendimento LIKE ?"
                params.append(f"%{atendimento}%")
            if nome:
                query += " AND nome LIKE ?"
                params.append(f"%{nome}%")

            # Executa a consulta
            cursor.execute(query, params)
            reclamacoes = cursor.fetchall()

        except Exception as e:
            print("Erro ao buscar dados:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template('buscar_reclamacoes.html', reclamacoes=reclamacoes)

@app.route('/outra_pagina')
def outra_pagina():
    username = session.get('username')
    return render_template('outra_pagina.html', username=username)


def buscar_reclamacao_por_id(id_reclamacao):
    conn = create_connection() # sua função para conectar ao banco de dados
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_reclamacao, data_final_reclamacao, nome, id_reclamacao, 
               motivo_legenda_reclamacao, ocorrencia, produto, nivel, 
               replica, resposta_publica, avaliacao, nota, 
               voltaria_fazer_negocio, caso_resolvido, o_que_houve_no_atendimento, 
               moderacao_solicitada, data_moderacao, motivo_moderacao, 
               moderacao_aceita, motivo_negativa, responsavel, segmento 
        FROM reclamacoesRa 
        WHERE id_reclamacao = ?
    """, (id_reclamacao,))

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return {
            'data_reclamacao': resultado[0],
            'data_final_reclamacao': resultado[1],
            'nome': resultado[2],
            'id_reclamacao': resultado[3],
            'motivo_legenda_reclamacao': resultado[4],
            'ocorrencia': resultado[5],
            'produto': resultado[6],
            'nivel': resultado[7],
            'replica': resultado[8],
            'resposta_publica': resultado[9],
            'avaliacao': resultado[10],
            'nota': resultado[11],
            'voltaria_fazer_negocio': resultado[12],
            'caso_resolvido': resultado[13],
            'o_que_houve_no_atendimento': resultado[14],
            'moderacao_solicitada': resultado[15],
            'data_moderacao': resultado[16],
            'motivo_moderacao': resultado[17],
            'moderacao_aceita': resultado[18],
            'motivo_negativa': resultado[19],
            'responsavel': resultado[20],
            'segmento': resultado[21]
        }
    return None


@app.route('/editar_reclamacao/<int:id>', methods=['GET'])
def editar_reclamacao(id):
    reclamacao = buscar_reclamacao_por_id(id)
    if reclamacao:
        return render_template('editar_reclamacao.html', reclamacao=reclamacao)
    return "Reclamação não encontrada", 404


@app.route('/atualizar_reclamacao/<int:id>', methods=['POST'])
def atualizar_reclamacao(id):
    data_reclamacao = request.form['data_reclamacao']
    data_final_reclamacao = request.form['data_final_reclamacao']
    nome = request.form['nome']
    motivo_legenda_reclamacao = request.form['motivo_legenda_reclamacao']
    ocorrencia = request.form['ocorrencia']
    produto = request.form['produto']
    nivel = request.form['nivel']
    replica = request.form['replica']
    resposta_publica = request.form['resposta_publica']
    avaliacao = request.form['avaliacao']
    nota = request.form['nota']
    voltaria_fazer_negocio = 'voltaria_fazer_negocio' in request.form
    caso_resolvido = 'caso_resolvido' in request.form
    o_que_houve_no_atendimento = request.form['o_que_houve_no_atendimento']
    moderacao_solicitada = 'moderacao_solicitada' in request.form
    data_moderacao = request.form['data_moderacao']
    motivo_moderacao = request.form['motivo_moderacao']
    moderacao_aceita = 'moderacao_aceita' in request.form
    motivo_negativa = request.form['motivo_negativa']
    responsavel = request.form['responsavel']
    segmento = request.form['segmento']

    conn = create_connection()  # sua função para conectar ao banco de dados
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reclamacoesRa SET 
            data_reclamacao = ?, 
            data_final_reclamacao = ?, 
            nome = ?, 
            motivo_legenda_reclamacao = ?, 
            ocorrencia = ?, 
            produto = ?, 
            nivel = ?, 
            replica = ?, 
            resposta_publica = ?, 
            avaliacao = ?, 
            nota = ?, 
            voltaria_fazer_negocio = ?, 
            caso_resolvido = ?, 
            o_que_houve_no_atendimento = ?, 
            moderacao_solicitada = ?, 
            data_moderacao = ?, 
            motivo_moderacao = ?, 
            moderacao_aceita = ?, 
            motivo_negativa = ?, 
            responsavel = ?, 
            segmento = ? 
        WHERE id_reclamacao = ?
    """, (data_reclamacao, data_final_reclamacao, nome, motivo_legenda_reclamacao, ocorrencia, produto, nivel,
          replica, resposta_publica, avaliacao, nota, voltaria_fazer_negocio, caso_resolvido,
          o_que_houve_no_atendimento, moderacao_solicitada, data_moderacao, motivo_moderacao,
          moderacao_aceita, motivo_negativa, responsavel, segmento, id))

    conn.commit()
    conn.close()
    return redirect(url_for('editar_reclamacao', id=id))


if __name__ == '__main__':
    app.run(debug=True)
