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
        
# Devuelve peliculas por ID o Titulo
@app.route("/api/peliculas/<data>", methods=['GET'])
def retornar_pelicula(data):
    if usuario_privado == True:
        # Devuelve pelicula por ID
        if data.isnumeric():
            peliculas = db["peliculas"]
            for pelicula in peliculas:
                if pelicula["id"] == int(data):
                    return jsonify(pelicula), HTTPStatus.OK
        # Devuelve pelicula por titulo
        else:
            pelicula = existe_pelicula(data)
            if pelicula:
                return jsonify(pelicula), HTTPStatus.OK
            return jsonify("El titulo no existe"), HTTPStatus.NOT_FOUND
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Funcion interna no flask
def existe_pelicula(titulo):
    peliculas = db["peliculas"]
    for pelicula in peliculas:
        if pelicula['titulo'].lower() == titulo.lower():
            return pelicula
    return False

# Carga una pelicula nueva
@app.route("/api/peliculas", methods=['POST'])
def alta_pelicula():
    if usuario_privado == True:
        # recibir datos por parte del cliente
        data = request.get_json()
        # validar data que viene del pedido
        # data.keys() >= {"usuario", "titulo"} retorna true si hay coincidencia

        campos = {"titulo", "anio", "genero", "genero_sub", "id_director", "sinopsis", "imagen", "trailer", "subidapor", "puntaje", "comentario"}
        if data.keys() < campos:
            return jsonify("Faltan campos en el pedido"), HTTPStatus.BAD_REQUEST

        if existe_pelicula(data["titulo"]):
            return jsonify("La pelicula ya existe en la base de datos."), HTTPStatus.BAD_REQUEST
        
        next_peli_id = int(db["peliculas"][-1]["id"]) + 1
        comentario_nuevo = {
            "id_usuario": data["subidapor"],
            "id_pelicula": next_peli_id,
            "comentario": data["comentario"],
            "puntaje": data["puntaje"]
        }
        db["comentarios"].append(comentario_nuevo)

        pelicula_nueva = {
            "id": next_peli_id,
            "titulo": data["titulo"],
            "anio": data["anio"],
            "genero": data["genero"],
            "genero_sub": data["genero_sub"],
            "id_director": data["id_director"],
            "sinopsis": data["sinopsis"],
            "imagen": data["imagen"],
            "trailer": data["trailer"],
            "subidapor": data["subidapor"],
            "promedio": data["puntaje"]
        }
        db["peliculas"].append(pelicula_nueva)
        print("Se cargo una pelicula nueva")
        return jsonify(pelicula_nueva), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Modifica una pelicula por ID
@app.route("/api/peliculas/<int:id>", methods=['PUT'])
def modificar_pelicula(id):
    if usuario_privado == True:
        encontrado = False
        data = request.get_json()
        for peli in db["peliculas"]:
            if peli["id"] == int(id):
                encontrado = True
                id_pelicula = peli["id"]
                promedio = recalcular_promedio(id_pelicula)
                
                peli["id"]= int(id)                                           
                peli["titulo"]= data["titulo"]
                peli["anio"]= int(data["anio"])
                peli["genero"]= data["genero"]
                peli["genero_sub"]= data["genero_sub"]
                peli["id_director"]= int(data["id_director"])
                peli["sinopsis"]= data["sinopsis"]
                peli["imagen"]=data["imagen"]
                peli[ "trailer"]= data["trailer"]
                peli["promedio"]= promedio
                peli["subidapor"]= int(data["subidapor"])
                
        if encontrado == True:
            print("Se modificaron datos de la pelicula")
            return jsonify("Se actualizaron los datos de la pelicula"), HTTPStatus.OK
        else:
            print("No se modificaron datos")
            return jsonify("No se actualizaron los datos de la película"), HTTPStatus.NOT_FOUND
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Funcion interna no flask
def recalcular_promedio(id_pelicula):
    puntajes = [coment["puntaje"] for coment in db["comentarios"] if coment["id_pelicula"] == int(id_pelicula)]
    if len(puntajes) == 0:
        return sum(puntajes)    
    return round(sum(puntajes) / len(puntajes), 1)

# Devuelve peliculas con portada
@app.route("/api/pelicula_portada", methods=['GET'])
def retornar_peliculas_con_portada():
    if usuario_privado == True:
        portadas = [peli for peli in db["peliculas"] if len(peli["imagen"]) > 0]
        print("Se mostraron las peliculas con portadas")
        return jsonify(portadas), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Borra una pelicula por ID - Pelicula 28 no tiene comentarios
@app.route("/api/peliculas", methods=['DELETE'])
def borrar_pelicula():
    if usuario_privado == True:
        # recibir datos por parte del cliente
        data = request.get_json()
        hay_comentarios= False
        for coment in db["comentarios"]:
            if coment["id_pelicula"] == data["id_pelicula"]:
                hay_comentarios=True
                
        if hay_comentarios == True:
            return jsonify("MAMA! Saca la mano de ahí carajo.(by el comandante Ricardo Fort) Hay comentarios de otros!"), HTTPStatus.BAD_REQUEST
        else:
            db["peliculas"] = [peli for peli in db["peliculas"] if peli["id"] != (int(data["id_pelicula"]))]
            return jsonify("Se borró la película"), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST
        
# Devuelve listado de directores
@app.route("/api/directores", methods=['GET'])
def retornar_directores():
    if usuario_privado == True:
        return jsonify(db["directores"])
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Carga un comentario nuevo
@app.route("/api/comentarios", methods=['POST'])
def cargar_comentario():
    if usuario_privado == True:
        data = request.get_json()
        campos = {"id_usuario", "id_pelicula", "comentario", "puntaje"}
        if data.keys() < campos:
            return jsonify("Faltan campos"), HTTPStatus.BAD_REQUEST
    
        comentario_nuevo = {
            "id_usuario": data["id_usuario"],
            "id_pelicula": data["id_pelicula"],
            "comentario": data["comentario"],
            "puntaje": data["puntaje"]
        }
        db["comentarios"].append(comentario_nuevo)
        return jsonify(comentario_nuevo), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve listado de comentarios
@app.route("/api/comentarios", methods=['GET'])
def todos_los_comentarios():
    if usuario_privado == True:
        return jsonify(db["comentarios"]), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve comentarios de las peliculas por ID de usuario
@app.route("/api/comentarios/<peli>/<user>", methods=['GET'])
def comentario_owner(peli, user):
    if usuario_privado == True:
        [comentario] = [coment for coment in db["comentarios"] if int(coment["id_usuario"]) == int(user) and int(coment["id_pelicula"]) == int(peli)]
        return jsonify(comentario), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

# Devuelve peliculas por genero
@app.route("/api/generos", methods=['GET'])
def obtener_generos():
    if usuario_privado == True:
        return jsonify(db["generos"]), HTTPStatus.OK
    else:
        return jsonify("Usted no es un usuario registrado"), HTTPStatus.BAD_REQUEST

if __name__=="__main__":
    app.run(debug=True)