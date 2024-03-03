import datetime
from flask import Flask, render_template, request, url_for, redirect, jsonify

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/livraria'

db = SQLAlchemy(app)

#--------------------------------------------
class Livros(db.Model): #cria tabela de livros no banco de dados 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100))
    autor = db.Column(db.String(100))
    editora = db.Column(db.String(100))
    genero = db.Column(db.String(100))
    quantidade = db.Column(db.Integer)
    ano = db.Column(db.Integer)

    def __init__(self, titulo, autor, editora, genero, quantidade, ano):
        self.titulo = titulo
        self.autor = autor
        self.editora = editora
        self.genero = genero
        self.quantidade = quantidade
        self.ano = ano
with app.app_context():  #não estava conseguindo usar db.create_all() sem isso
    db.create_all()
#--------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route("/cadastrar", methods = ['POST', 'GET']) #cadastra um novo livro
def cadastrar():
    if request.method == 'POST':
        titulo = (request.form.get("titulo"))
        autor = (request.form.get("autor"))
        editora = (request.form.get("editora"))
        genero = (request.form.get("genero"))
        quantidade = (request.form.get("quantidade"))
        ano = (request.form.get("ano"))

        if titulo and autor and editora and genero and quantidade and ano:
            livro = Livros(titulo, autor, editora, genero, quantidade, ano)
            db.session.add(livro)
            db.session.commit()
        else:
            return "Erro ao cadastrar livro"
    return redirect(url_for("index"))


@app.route('/listar') #lista todos os livros cadastrados
def listar():
    livros = Livros.query.all()
    return render_template('lista.html', livros=livros)        


@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    if request.method == 'POST':
        livro = Livros.query.filter_by(id=id).first()
        db.session.delete(livro)
        db.session.commit()

        livros = Livros.query.all()
    return redirect(url_for('listar', livros=livros))



@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    livro = Livros.query.filter_by(id=id).first()
    if request.method == 'POST':
        titulo = request.form.get("titulo")
        autor = request.form.get("autor")
        editora = request.form.get("editora")
        genero = request.form.get("genero")
        quantidade = request.form.get("quantidade")
        ano = request.form.get("ano")

        if titulo and autor and editora and genero and quantidade and ano:
            livro.titulo = titulo
            livro.autor = autor
            livro.editora = editora
            livro.genero = genero
            livro.quantidade = quantidade
            livro.ano = ano
            db.session.commit()

            return redirect(url_for("listar"))        

        else:
            return "Erro ao editar livro"
    return render_template('editar.html', livro=livro)

@app.route('/pesquisar')
def pesquisar_livros():
    termo_pesquisa = request.args.get('titulo')
    if termo_pesquisa:
        livros_encontrados = Livros.query.filter(Livros.titulo.like(f'%{termo_pesquisa}%')).all()
        return render_template('resultados_pesquisa.html', livros=livros_encontrados, termo_pesquisa=termo_pesquisa)
    else:
        return jsonify({'error': 'Por favor, forneça um termo de pesquisa válido.'}), 400


if __name__ == '__main__':
    app.run(debug=True)