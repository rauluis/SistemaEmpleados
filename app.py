from flask import Flask
from flask import render_template, request, redirect, url_for, flash, jsonify
from flaskext.mysql import MySQL
from flask import send_from_directory

from datetime import datetime
import os

# Create a flask application
app = Flask(__name__)


#llave secretitaaaa owo
app.secret_key = 'SecretaOwO'


mysql = MySQL()
# MySQL configurations




app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'
app.config['MYSQL_DATABASE_PORT'] = 3307
#inicar la conexion con la base de datos con init_app con todas las configuracion que se declaron en app
mysql.init_app(app)
#crear una referencia de la carpeta 
CARPETA = os.path.join('uploads')
#Crear una referencia a una variable  para almacenar la ruta especifica anterior "uploads". Para poder acceder despues.
app.config['CARPETA'] = CARPETA



#crear un acceso a la carpeta uploads con una url. Accediendo a la carpeta de acceso que se creo. 
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

# crear un ruteo para la raiz de la aplicacion, accedio directo con un "/".
# indenfica la carpeta empleados y se va a buscar el archivo index.html
@app.route('/')
def index():
    #instruccion sql para hacer pruebas 
    sql = "SELECT * FROM `empleados`;"
    #la instruccion sql se conectara con mysql que se creo con la configuracion previa
    conn = mysql.connect()
    #se crea un cursor para hacer las consultas
    cursor = conn.cursor()
    #se ejecuta la instruccion sql
    cursor.execute(sql)
    #cursor toda la informacion que se obtuvo . fetchall() regresamela conjuntamente 
    empleados = cursor.fetchall()
    #print(empleados)

    #cerrar la conexion con commit
    conn.commit()
    #enviar informacion a la vista con 'render_template' despues de la ",". Enviar una variable con el valor de empleados.
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    #seleccion de datos para eliminar foto
    cursor.execute("SELECT foto FROM empleados WHERE id=%s",(id))
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))


    #instruccion sql para eliminar un registro con un id especifico
    cursor.execute("DELETE FROM `empleados` WHERE `id` = %s;",(id))
    conn.commit()
    #una vez que se elimino el registro, se redirecciona a la ruta de donde veniste /
    return redirect('/')
    
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `empleados` WHERE `id` = %s;",(id))
    empleados = cursor.fetchall()
    conn.commit()

    return render_template('empleados/edit.html',empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    _id = request.form['txtId']

   
    sql = "UPDATE empleados SET nombre = %s, correo = %s WHERE id = %s;"
    datos = (_nombre, _correo,_id)
   
    conn = mysql.connect()
    cursor = conn.cursor() 

    now= datetime.now()
    tiempo = now.strftime("%Y%H%M%S")


    if _foto.filename != '':
        nuevoNombreFoto= tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        #recuperar la foto y actualizar solo ese campo de foto
        cursor.execute("SELECT foto FROM empleados WHERE id=%s",(_id))
        #buscamos esa foto para poder removerla
        fila = cursor.fetchall()
        #sistema operativo. remove. Usar el path, join para unir la carpeta desde app.config y se va a unir con la fila 
        # de la base de datos [0] [0], significa el nombre de la foto
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        #actualizar unicamente la foto  cuando el id sea igual al nuevoNombreFoto y tambien actualizar usando el id.
        cursor.execute("UPDATE empleados set foto =%s where  id= %s",(nuevoNombreFoto,_id))
        conn.commit()


    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')


#Toda la infromacion se enviara por el metodo post a /store

@app.route('/store', methods=['POST'])
def storage():
    #permite conectar con la base de datos y despues redireccionar 
    #pasar informacion del formulario a la consulta sql
    #_nombre  adquiere el valor del campo nombre del formulario...
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    #validacion de campos vacios de nombre, correo o foto
    #se usa flash para mostrar mensajes en la vista de create. El template usa redirect para redireccionar create
    if _nombre== '' or _correo == '' or _foto== '':
        flash('Recuerda llenar todos los campos')   
        return redirect(url_for('create'))


    #concatener la fecha y hora actual al nombre del archivo de la foto
    now= datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    #si la foto no esta vacia, se concatena el tiempo al nombre del archivo y se guarda en la carpeta uploads con el nuevoNombreFoto
    if _foto.filename != '':
        nuevoNombreFoto= tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    

    #%s se acomodara en orden de los parametros que se le pase 
    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s);"
    
    datos = (_nombre, _correo, nuevoNombreFoto)
   
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')







#python requiere que el archivo principal sea el main, corre el programa con el debugger y se ejecuta el main
if __name__ == '__main__':
    app.run(debug=True)

# para ejecutar el programa en el servidor, se debe ejecutar con el comando: python app.py
