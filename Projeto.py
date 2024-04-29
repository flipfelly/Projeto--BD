import time
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, url_for, redirect, jsonify, flash 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func
from flask_admin import Admin
from flask_login import login_required, UserMixin, LoginManager, login_user, logout_user, current_user

app = Flask(__name__)



login_manager = LoginManager(app)


#conexão com o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/teste'
app.config['SECRET_KEY'] = '123456'

db = SQLAlchemy(app)

class Autor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))

    def __init__(self, nome):
        self.nome = nome

class Editora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))

    def __init__(self, nome):
        self.nome = nome

class Genero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))

    def __init__(self, nome):
        self.nome = nome

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)
    ano = db.Column(db.Integer)
    preco = db.Column(db.Float)
    autor_id = db.Column(db.Integer, db.ForeignKey('autor.id'))
    editora_id = db.Column(db.Integer, db.ForeignKey('editora.id'))
    genero_id = db.Column(db.Integer, db.ForeignKey('genero.id'))

    autor = db.relationship('Autor', backref=db.backref('livros', lazy=True))
    editora = db.relationship('Editora', backref=db.backref('livros', lazy=True))
    genero = db.relationship('Genero', backref=db.backref('livros', lazy=True))

    def __init__(self, titulo, quantidade, ano, preco, autor_id, editora_id, genero_id):
        self.titulo = titulo
        self.quantidade = quantidade
        self.ano = ano
        self.preco = preco
        self.autor_id = autor_id
        self.editora_id = editora_id
        self.genero_id = genero_id
#-------------------------------------------- Implementando classe cliente, pedido e vendedor

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    onepiece_fan = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #chave estrangeira

    user = db.relationship('User', backref=db.backref('cliente', lazy=True))

    def __init__(self, nome, cpf, email, telefone, time, onepiece_fan, user_id):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.telefone = telefone
        self.time = time
        self.onepiece_fan = onepiece_fan
        self.user_id = user_id

class Funcionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #chave estrangeira

    user = db.relationship('User', backref=db.backref('funcionario', lazy=True))

    def __init__(self,email, nome, cpf, user_id ):
        self.email = email
        self.nome = nome
        self.cpf = cpf
        self.user_id = user_id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False, default='cliente')

    def __init__(self, email, senha, tipo):
        self.email = email
        self.senha = senha
        self.tipo = tipo


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id')  , nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionario.id'), nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_venda = db.Column(db.Date, nullable=False, default=func.now())

    cliente = db.relationship('User', backref=db.backref('vendas', lazy=True))
    livro = db.relationship('Livro', backref=db.backref('vendas', lazy=True))
    funcionario = db.relationship('Funcionario', backref=db.backref('vendas', lazy=True))

    def __init__(self, user_id, livro_id, quantidade, funcionario_id, forma_pagamento, valor):
        self.user_id = user_id
        self.livro_id = livro_id
        self.quantidade = quantidade
        self.funcionario_id = funcionario_id
        self.forma_pagamento = forma_pagamento
        self.valor = valor
       
with app.app_context():
    db.create_all()


@app.route('/')
def index(): #read
    termo_pesquisa = request.args.get('termo_pesquisa')
    valor_min = request.args.get('valor_min')
    valor_max = request.args.get('valor_max')
    estoque_baixo = request.args.get('estoque_baixo')
    ano_publicacao = request.args.get('ano_publicacao')
    genero = request.args.get('genero')

    query = Livro.query

    if genero:  # Alterado para 'genero_nome'
        query = query.join(Genero).filter(Genero.nome.like(f'%{genero}%'))

    if termo_pesquisa:
        query = query.filter(Livro.titulo.like(f'%{termo_pesquisa}%'))

    if valor_min:
        query = query.filter(Livro.preco >= float(valor_min))

    if valor_max:
        query = query.filter(Livro.preco <= float(valor_max))

    if ano_publicacao:
        query = query.filter(Livro.ano == int(ano_publicacao))

    if estoque_baixo: # Se a opção de filtragem de estoque baixo estiver ativada
        query = query.filter(Livro.quantidade <= 5)

    livros = query.all()

    tipo_usuario = request.args.get('tipo_usuario', default='cliente')  # Defina o tipo de usuário como 'cliente' por padrão

    funcionarios = Funcionario.query.all()

    cliente = Cliente.query.filter_by(user_id=current_user.id).first() if current_user.is_authenticated else None

    return render_template('index.html', livros=livros, tipo_usuario=tipo_usuario, funcionarios=funcionarios, current_user=current_user, cliente = cliente)

pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        user = User.query.filter_by(email=email).first()
        
        if user and user.senha == senha:
            # Login bem-sucedido
            login_user(user)
            tipo = user.tipo
            return redirect(url_for('index'))
        else:
            mensagem = "Email ou senha incorretos"
            return render_template('login.html', mensagem=mensagem)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('index'))


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route("/cadastrar", methods=['POST'])
def cadastrar(): #create
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        quantidade = request.form.get("quantidade")
        ano = request.form.get("ano")
        preco = request.form.get("preco")
        autor_nome = request.form.get("autor")
        editora_nome = request.form.get("editora")
        genero_nome = request.form.get("genero")

        autor = Autor.query.filter_by(nome=autor_nome).first()
        if not autor: #caso o autor não exista, ele é criado
            autor = Autor(nome=autor_nome)
            db.session.add(autor)

        editora = Editora.query.filter_by(nome=editora_nome).first()
        if not editora:
            editora = Editora(nome=editora_nome)
            db.session.add(editora)

        genero = Genero.query.filter_by(nome=genero_nome).first()
        if not genero:
            genero = Genero(nome=genero_nome)
            db.session.add(genero)

        db.session.commit()

        livro = Livro(titulo=titulo, quantidade=quantidade, ano=ano, preco=preco, autor_id=autor.id, editora_id=editora.id, genero_id=genero.id)
        db.session.add(livro)
        db.session.commit()

        mensagem = "Livro cadastrado com sucesso!"
        return render_template("cadastro.html", mensagem=mensagem)

    return render_template("cadastro.html")

@app.route('/cadastro_pessoa')
def cadastro_pessoa():
    return render_template('Login.html', current_user=current_user, )

@app.route("/cadastrar_pessoa", methods=['GET', 'POST'])
def cadastrar_pessoa():
    if request.method == 'POST':
        nome = request.form.get('Nome')
        cpf = request.form.get('CPF')
        email = request.form.get('E-mail')
        senha = request.form.get('senha') 
        telefone = request.form.get('Telefone')
        time = request.form.get('time')
        onepiece_fan = True if request.form.get('OnePiece') else False
        tipo = request.form.get('tipo')

        # Verifica se o CPF já está cadastrado
        if Cliente.query.filter_by(cpf=cpf).first() or Funcionario.query.filter_by(cpf=cpf).first() or Cliente.query.filter_by(email=email).first() or Funcionario.query.filter_by(email=email).first():
            mensagem = "Email ou cpf já está cadastrado."
        
            return render_template("cadastro_user.html", mensagem=mensagem)
            
        else:

            if tipo == 'funcionario':
                novo_user = User(email=email, senha=senha, tipo='funcionario')
                db.session.add(novo_user)
                db.session.commit()

                novo_funcionario = Funcionario(email=email, nome=nome, cpf=cpf, user_id=novo_user.id)
                db.session.add(novo_funcionario)
                db.session.commit()

            else:
                novo_user = User(email=email, senha=senha, tipo='cliente')
                db.session.add(novo_user)
                db.session.commit()

                novo_cliente = Cliente(nome=nome, cpf=cpf, email= email, telefone=telefone, time=time, onepiece_fan=onepiece_fan, user_id=novo_user.id)
                db.session.add(novo_cliente)
                db.session.commit()


                
            mensagem = "Pessoa cadastrada com sucesso!"
            return render_template("cadastro_user.html", mensagem=mensagem)

    return render_template("cadastro_user.html")


@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id): #delete
    if request.method == 'POST':
        livro = Livro.query.filter_by(id=id).first()
        db.session.delete(livro)
        db.session.commit()

        livros = Livro.query.all()
    return redirect(url_for('index', livros=livros))

@app.route('/comprar/<int:id>', methods=['POST'])
def comprar(id):
    if request.method == 'POST':
        livro = Livro.query.get(id)
        quantidade = int(request.form.get('quantidade'))
        forma_pagamento = request.form.get('forma_pagamento')
        funcionario_id = request.form.get('vendedor')
        user_id = current_user.id

        cliente = Cliente.query.filter_by(user_id=user_id).first()


        if livro.quantidade >= quantidade:
            livro.quantidade -= quantidade
            db.session.commit()
            # Calcular o valor total da compra
            valor_total = livro.preco * quantidade

            # Verificar se o cliente tem direito a desconto
            if cliente.time == 'flamengo' or cliente.onepiece_fan:
                desconto = valor_total * 0.1
                valor_total = valor_total - desconto

            # Salvar informações da compra no banco de dados
            nova_venda = Venda(livro_id=id, quantidade=quantidade, user_id=user_id, forma_pagamento=forma_pagamento, funcionario_id=funcionario_id, valor=valor_total)
            db.session.add(nova_venda)
            db.session.commit()
            flash('Compra realizada com sucesso!')
            # Redirecionar para a página inicial com o valor total da compra como parâmetro de consulta na URL
            return redirect(url_for('index', total_compra=valor_total))
        else:
            flash('Quantidade indisponível', 'error')
            return redirect(url_for('index'))
    return render_template('Login.html')



@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id): #update
    livro = Livro.query.get(id)
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        autor_nome = request.form.get("autor_nome")
        editora_nome = request.form.get("editora_nome")
        genero_nome = request.form.get("genero_nome")
        quantidade = request.form.get("quantidade")
        ano = request.form.get("ano")
        preco = request.form.get("preco")

        if titulo and autor_nome and editora_nome and genero_nome and quantidade and ano:
            # Procurar autor pelo nome
            autor = Autor.query.filter_by(nome=autor_nome).first()
            if not autor:
                autor = Autor(nome=autor_nome)
                db.session.add(autor)

            # Procurar editora pelo nome
            editora = Editora.query.filter_by(nome=editora_nome).first()
            if not editora:
                editora = Editora(nome=editora_nome)
                db.session.add(editora)

            # Procurar gênero pelo nome
            genero = Genero.query.filter_by(nome=genero_nome).first()
            if not genero:
                genero = Genero(nome=genero_nome)
                db.session.add(genero)

            livro.titulo = titulo
            livro.autor = autor
            livro.editora = editora
            livro.genero = genero
            livro.quantidade = quantidade
            livro.ano = ano
            livro.preco = preco
            db.session.commit()

            return redirect(url_for("index"))        

        else:
            return "Erro ao editar livro"
    return render_template('editar.html', livro=livro)



@app.route('/livro_aleatorio')
def livro_aleatorio():
    livros = Livro.query.all()
    if not livros:
        return render_template('detalhes_livro.html', mensagem="Não há livros cadastrados")
    else:
        livro_aleatorio = random.choice(livros)
        return render_template('detalhes_livro.html', livro=livro_aleatorio)

@app.route('/relatorio')
def relatorio():
    total_cadastrados = Livro.query.count()
    livros_no_estoque = Livro.query.with_entities(db.func.sum(Livro.quantidade)).scalar()
    valor_total_estoque = round(Livro.query.with_entities(db.func.sum(Livro.quantidade * Livro.preco)).scalar(), 2) #arredondar para 2 casas decimais
    return render_template('relatorio.html', total_cadastrados=total_cadastrados, livros_no_estoque=livros_no_estoque, valor_total_estoque=valor_total_estoque)  

@app.route('/dados_cadastro')
def dados_cadastrais():
    id = current_user.id 
    cliente = Cliente.query.filter_by(user_id=id).first()
    vendas = Venda.query.filter_by(user_id=id).all()

    return render_template('Dados_cliente.html', cliente = cliente, vendas =vendas)

@app.route('/relatorio_mensal') 
def relatorio_mensal():
    ano, mes = time.strftime('%Y'), time.strftime('%m')

    if request.args.get('ano'):
        ano = request.args.get('ano')
    if request.args.get('mes'):
        mes = request.args.get('mes')

    mes_ano = f"{ano}-{mes:02}"  # Formatar o mês para adicionar um zero à esquerda, se necessário
    
    cursor = db.session.connection().connection.cursor()
    cursor.callproc('GerarRelatorioMensal', [mes_ano])
    relatorio = cursor.fetchall()
    cursor.close()

    return render_template('relatorio_mensal.html', relatorio=relatorio)

if __name__ == '__main__':
    app.run(debug=True)