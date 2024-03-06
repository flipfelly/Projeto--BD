import random

from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/livraria'

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

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    termo_pesquisa = request.args.get('termo_pesquisa')
    livros = Livro.query.all()
    if termo_pesquisa:
        livros = Livro.query.filter(Livro.titulo.like(f'%{termo_pesquisa}%')).all()
    return render_template('index.html', livros=livros) 

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        quantidade = request.form.get("quantidade")
        ano = request.form.get("ano")
        preco = request.form.get("preco")
        autor_nome = request.form.get("autor")
        editora_nome = request.form.get("editora")
        genero_nome = request.form.get("genero")

        autor = Autor.query.filter_by(nome=autor_nome).first()
        if not autor:
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

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if request.method == 'POST':
        livro = Livro.query.filter_by(id=id).first()
        db.session.delete(livro)
        db.session.commit()

        livros = Livro.query.all()
    return redirect(url_for('index', livros=livros))



@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
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


@app.route('/pesquisar', methods=['POST'])
def pesquisar_livros():
    termo_pesquisa = request.form.get('titulo')
    if termo_pesquisa:
        livros_encontrados = Livro.query.filter(Livro.titulo.like(f'%{termo_pesquisa}%')).all()
        return render_template('resultados_pesquisa.html', livros=livros_encontrados, termo_pesquisa=termo_pesquisa)
    else:
        return redirect(url_for('/'))

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
    valor_total_estoque = Livro.query.with_entities(db.func.sum(Livro.quantidade * Livro.preco)).scalar()
    return render_template('relatorio.html', total_cadastrados=total_cadastrados, livros_no_estoque=livros_no_estoque, valor_total_estoque=valor_total_estoque)  



if __name__ == '__main__':
    app.run(debug=True)
