from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import mysql.connector

app = Flask(__name__)
app.secret_key = 'p@ssword'  # Asegúrate de cambiar esto por una clave segura en un entorno de producción

# Conexión a la base de datos
db = mysql.connector.connect(
    host="mysql-santipvzz.alwaysdata.net",
    user="santipvzz",
    password="S@ntulin12",
    database="santipvzz_users"
)

cursor = db.cursor()

# Función decoradora para requerir inicio de sesión
def login_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))  # O la ruta que maneja el inicio de sesión
        return route_function(*args, **kwargs)
    return decorated_function

# Función auxiliar para obtener los datos de un usuario por correo electrónico
def get_user_by_email(email):
    query = f"SELECT * FROM datos WHERE email = '{email}'"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        user_data = dict(zip(cursor.column_names, result))
        return user_data
    else:
        return None

# Función auxiliar para verificar si un correo ya está registrado
def is_email_registered(email):
    query = f"SELECT * FROM datos WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchone() is not None

# Ruta para mostrar la lista de juegos (requiere inicio de sesión)
@app.route('/game')
@login_required
def show_games():
    # Aquí puedes obtener la lista de juegos disponibles desde la base de datos o definirla estáticamente
    games = ['Pacman', 'Coches']

    return render_template('game_selection.html', games=games)

# Ruta para el registro de usuarios
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if len(name) >= 1 and len(email) >= 1 and len(password) >= 1:
            if is_email_registered(email):
                return render_template('register.html', message='¡El correo ya está registrado!', css_class='bad')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            fechareg = datetime.now().strftime('%d/%m/%Y')
            query = "INSERT INTO datos(nombre, email, password, fecha_reg) VALUES (%s, %s, %s, %s)"
            values = (name, email, hashed_password, fechareg)
            try:
                cursor.execute(query, values)
                db.commit()
                return render_template('register.html', message='¡Registro exitoso!', css_class='good')
            except Exception as e:
                db.rollback()
                print(f"Error during registration: {str(e)}")
                return render_template('register.html', message='¡Ups ha ocurrido un error!', css_class='bad')
        else:
            return render_template('register.html', message='¡Por favor complete los campos!', css_class='bad')

    return render_template('register.html')

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if len(email) >= 1 and len(password) >= 1:
            user_data = get_user_by_email(email)

            if user_data and check_password_hash(user_data['password'], password):
                session['user_email'] = email  # Almacenar el correo electrónico del usuario en la sesión
                return redirect('/game')

            return render_template('login.html', login_message='¡Credenciales incorrectas!', login_css_class='bad')

        return render_template('login.html', login_message='¡Por favor, ingrese correo y contraseña!', login_css_class='bad')

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('user_email', None)
    return redirect('/login')

# Ruta para jugar un juego seleccionado (requiere inicio de sesión)
@app.route('/play/<game>')
@login_required
def play_game(game):
    # Lógica para cargar el juego seleccionado
    # Puedes redirigir al juego correspondiente o cargar su página principal
    if game == 'Pacman':
        return send_from_directory('game', 'index.html')
    elif game == 'Coches':
        return send_from_directory('game1', 'index.html')
    else:
        return render_template('game_selection.html', game=game)

if __name__ == '__main__':
    app.run(debug=True)


