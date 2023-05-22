from flask import Flask, render_template, request, redirect
import mysql.connector
import os

app = Flask(__name__)
# Caminho absoluto do diretório 'templates'
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)
print("Caminho absoluto do diretório de modelos:", template_dir)


def connect_to_database():
    return mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_DATABASE'],
        port=os.environ['DB_PORT']
    )


def verificar_credenciais(username, password):
    # Conectar ao banco de dados
    connection = connect_to_database()
    cursor = connection.cursor()

    # Consulta SQL para verificar as credenciais
    query = "SELECT * FROM customer_account WHERE login = %s AND senha = %s"
    cursor.execute(query, (username, password))

    # Verificar se as credenciais são válidas
    resultado = cursor.fetchone()

    # Fechar a conexão com o banco de dados
    cursor.close()
    connection.close()

    return resultado is not None

# Rota para exibir a página de login
@app.route('/')
def index():
    return render_template('login.html')

# Rota para processar o formulário de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar as credenciais no banco de dados
        if verificar_credenciais(username, password):
            # Credenciais válidas, redirecionar para a página de investimentos
            return redirect('/invest_page?username=' + username)
        else:
            # Credenciais inválidas, exibir mensagem de erro
            return render_template('login.html', error='Credenciais inválidas')
    else:
        return redirect('/')

# Rota para a página de investimentos após o login
@app.route('/invest_page')
def invest_page():
    username = request.args.get('username')

    # Obtém os contratos do cliente do banco de dados
    connection = connect_to_database()
    cursor = connection.cursor()

    # Consulta SQL para obter os contratos do cliente
    query = """
        SELECT 
            contract.id,
            CONCAT('R$ ' ,FORMAT(SUM(contract.amount),2)) AS 'Total Investido',
            CONCAT('R$ ', FORMAT(SUM(contract.current_amount),2)) AS 'Total Atual',
            CONCAT('R$ ', FORMAT(SUM(contract.gc_total_profit),2)) AS 'Total Lucro'
        FROM 
            contract 
        WHERE 
            contract.active = 1 
            AND id_client = (SELECT id_client FROM customer_account WHERE login = %s)
        GROUP BY
            id_client
    """
    cursor.execute(query, (username,))
    contracts = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('invest_page.html', username=username, contracts=contracts)

if __name__ == '__main__':
    app.run(debug=True)
