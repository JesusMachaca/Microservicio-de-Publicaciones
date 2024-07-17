import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
import datetime
import psycopg2

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Configuración de conexión para PostgreSQL
conn_str = {
    "host": "dpg-cqarlkuehbks73de8dlg-a.oregon-postgres.render.com",
    "database": "bdfisitweet",
    "user": "grupo_app",
    "password": "4fPiWKsmtrNfCeHEEo2jBVIP7jvLGAn3"
}

# Conexión a la base de datos PostgreSQL
try:
    mydb = psycopg2.connect(**conn_str)
    print("Conexión exitosa a la base de datos PostgreSQL")
except Exception as e:
    print(f"No se pudo conectar a la base de datos PostgreSQL: {e}")

@app.route('/')
def Index():
    publicaciones = consultarTodasPublicaciones()
    return render_template('index.html', publicaciones=publicaciones)

@app.route('/registro-publicacion')
def page_registro_publicacion():
    if 'logged_in' in session:
        return render_template('registro-publicacion.html')
    else:
        flash("Debe iniciar sesión para agregar una publicación.")
        return redirect(url_for('login_render'))

@app.route('/agregar-publicacion', methods=['POST'])
def agregar_publicacion():
    if 'logged_in' in session:
        if request.method == 'POST':
            try:
                fecha = str(datetime.datetime.now())
                idAlumno = session['usuario_id']
                contenido = request.form['contenido']

                cursor = mydb.cursor()
                query = "INSERT INTO publicaciones (idAlumno, contenido, fecha) VALUES (%s, %s, %s)"
                values = (idAlumno, contenido, fecha)
                cursor.execute(query, values)
                mydb.commit()
                cursor.close()

                flash("Se ha registrado de manera correcta!")
            except Exception as e:
                flash(f"Error al realizar el registro: {e}")
        return redirect(url_for('page_registro_publicacion'))
    else:
        flash("Debe iniciar sesión para agregar una publicación.")
        return redirect(url_for('login_render'))

@app.route('/publicaciones/<int:idAlumno>')
def consultarPublicaciones(idAlumno):
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT contenido, fecha
            FROM publicaciones WHERE idAlumno = %s
        '''
        values = (idAlumno,)
        cursor.execute(query, values)
        resultados = cursor.fetchall()
        cursor.close()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/sesiones/<int:idAlumno>')
def consultarSesiones(idAlumno):
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT idLog, fecha
            FROM logs WHERE idAlumno = %s
        '''
        values = (idAlumno,)
        cursor.execute(query, values)
        resultados = cursor.fetchall()
        cursor.close()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'error': str(e)})

def consultarTodasPublicaciones():
    try:
        cursor = mydb.cursor()
        query = '''
            SELECT alumnos.nombre, alumnos.correo, publicaciones.contenido, publicaciones.fecha
            FROM alumnos
            JOIN publicaciones ON alumnos.idAlumno = publicaciones.idAlumno
        '''
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    except Exception as e:
        flash(f"Error al consultar publicaciones: {e}")
        return None

if __name__ as "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
