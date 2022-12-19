from http import HTTPStatus 
from flask import Flask, jsonify, request
import webbrowser
import json

app = Flask(__name__)

data = open("db.json", encoding="utf-8")
db = json.load(data)

@app.route('/api')
def api_docs():
    webbrowser.open("https://documenter.getpostman.com/view/24191361/2s8YzZPeCp")
    return jsonify("Documentación Postman"), HTTPStatus.OK

usuario_privado = False
print("Bienvenidos a Pelis.Py")
print("Estas registrado en esta pagina?")

validar_registro = input("Ingresa Si o No: ")
lower_input = validar_registro.lower()
if lower_input != "si":
    print ("Como usuario publico solo podes ver los titulos de las ultimas 10 peliculas")
    # Devuelve los titulos de las ultimas 10 peliculas
    for peli in db["peliculas"][-10:]:
        print(peli["titulo"], end="\n")
    print("Gracias por visitarnos!!!")
else: # Ingreso del usuario privado
    ingreso_usuario = input( "Ingrese su usuario: ")
    ingreso_contrasenia= input( "Ingrese su contraseña: ")
    for user in db["usuarios"]:
        if user["usuario"] == ingreso_usuario and user["contrasenia"] == ingreso_contrasenia:
            print("Usuario logueado con exito")
            print("Arranca tu experiencia como usuario registrado")
            usuario_privado = True

# Devuelve la informacion completa de las ultimas 10 peliculas - Usuario registrado
@app.route("/api/ultimas", methods=['GET'])
def retornar_peliculas():
    if usuario_privado == True:
        ultimas = db["peliculas"][-10:]
        pelis = []
        for peli in ultimas:
            peli["director"] = [dire for dire in db["directores"] if dire["id_director"] == peli["id_director"]]
            peli["comentarios"] = [coment for coment in db["comentarios"] if coment["id_pelicula"] == peli["id"]]
            for coment in peli["comentarios"]:
                [usuario] = [user for user in db["usuarios"] if user["id"] == coment["id_usuario"]]
                coment["nombre"] = usuario["nombre"]
            pelis.append(peli)
        print("Se mostro la informacion completa de las ultimas 10 peliculas")
        return jsonify(pelis), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve listado de usuarios
@app.route("/api/usuarios", methods=['GET'])
def retornar_usuarios():
        if usuario_privado == True:
            return jsonify(db["usuarios"]), HTTPStatus.OK
        else:
            return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve usuarios por ID
@app.route("/api/usuarios/<id>", methods=['GET'])
def retornar_usuario(id):
    if usuario_privado == True:
        usuarios = db["usuarios"]
        usuario_id = int(id)
        for usuario in usuarios:
            if usuario["id"] == usuario_id:
                return jsonify(usuario), HTTPStatus.OK
        return jsonify("Usuario inexistente"), HTTPStatus.BAD_REQUEST
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve listado de peliculas
@app.route("/api/peliculas", methods=['GET'])
def retornar_todas_peliculas():
    if usuario_privado == True:
        todas = db["peliculas"]
        peliculas = []
        for peli in todas:
            peli["director"] = [dire for dire in db["directores"] if dire["id_director"] == peli["id_director"]]
            peli["comentarios"] = [coment for coment in db["comentarios"] if coment["id_pelicula"] == peli["id"]]
            for coment in peli["comentarios"]:
                [usuario] = [user for user in db["usuarios"] if user["id"] == coment["id_usuario"]]
                coment["nombre"] = usuario["nombre"]
            peliculas.append(peli)
        print("Se mostro el listado de todas las peliculas")
        return jsonify(peliculas)
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST
