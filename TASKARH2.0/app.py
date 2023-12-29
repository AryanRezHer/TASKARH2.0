import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user

app = Flask(__name__)
#Path para encontrar la base de datos(primero obtenemos donde estamos y despues añadimos el nombre de los archivos)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'usuarios.db')
app.secret_key = 'proyecto2'

#Inicializamos Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
#Inicializamos SQLAlchemy
db = SQLAlchemy(app)

#delcalracion de clases 
class usuarios(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class list_task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

#This callback is used to reload the user object from the user ID stored in the session.
#It should take the str ID of a user, and return the corresponding user object.
@login_manager.user_loader
def load_user(user_id):
    return usuarios.query.get(user_id)

#creamos ruta principal
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST': #comprobamos si es un metodo post
        usr = request.form['username'] #recibimos los valores de los inputs
        pwd = request.form['password']
        if usr and pwd:
            try:
                usuario = usuarios.query.filter_by(username=usr,password=pwd).first() #el primero que encuentre
                user_id = usuario.id
                login_user(usuario)
                return redirect(url_for('listas', id=user_id))
            except AttributeError:
                mensaje = 'No esta en la DB. Por favor, registrate'               
                return render_template('singup.html', mensaje = mensaje)
            
        
    return render_template('index.html')
    

@app.route('/singup', methods=['GET','POST'])
def singup(): #Registramos usuario en BD
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']
        if usr and pwd:
            new_usr = usuarios(username=usr, password=pwd)
            db.session.add(new_usr) #añadimos datos a la db
            db.session.commit() #ceramos sesion
            return redirect(url_for('login'))
        else:
            return render_template('singup.html')
    else:
        return render_template('singup.html')
    
@app.route('/logout')
@login_required #obligatorio estar logeado
def logout():
    message = 'Adios ' + current_user.username + ' ;('
    logout_user()
    return render_template('index.html', message = message)

@app.route('/listas/<int:id>')
@login_required
def listas(id):
    user_id = current_user.id
    tasks = list_task.query.filter_by(usuario_id=user_id)
    return render_template('listas.html', lista = tasks)

@app.route('/addtask', methods=['POST'])
def addtask():
    user_id = current_user.id
    content=request.form['envio']
    if content:
        task = list_task(content=content, done=False, usuario_id=user_id)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('listas',id=user_id))
    
    return redirect(url_for('listas',id=user_id))

@app.route('/deltask/<id>')
@login_required
def deltask(id):
    user_id = current_user.id
    deltask = list_task.query.filter_by(id=int(id)).first()
    db.session.delete(deltask)
    db.session.commit()
    return redirect(url_for('listas',id=user_id))

@app.route('/donetask/<id>')
@login_required
def donetask(id):
    user_id = current_user.id
    donetask = list_task.query.filter_by(id=int(id)).first()
    donetask.done = not(donetask.done)
    db.session.commit()
    return redirect(url_for('listas',id=user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()#crear tablas
    app.run(debug=True)