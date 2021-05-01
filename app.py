###########Librerias
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import pymongo, json, requests, urllib.request, matplotlib
from bson.objectid import ObjectId 
from bson.json_util import dumps, loads
from datetime import datetime

###########Conexion a DB
client = pymongo.MongoClient("localhost", 27017)
db = client.SistemaDeFabrica

###########Crear App
app = Flask(__name__)
app.secret_key = "key"

###########Funciones
def verificar_permiso():
    if "user" in session:
        return True
    else:
        return False

def notificar_envio(orden):
    cliente = db.ordenes.find_one({"_id":ObjectId(orden)})['cliente']
    url = str(db.clientes.find_one({"_id":cliente})) + "/api_war/api/actualizarEstado/"
    data = {"orden":orden}
    response = requests.post(url, json = data)
    return True

###########Directorio de paginas
#HomePage
@app.route("/")
def home_page():
    return render_template("main.html")

#Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        tuser = request.form["user"]
        tpassword = request.form["pass"]
        verificarcion_de_usuario = db.usuarios.find_one({'usuario':tuser, 'password':tpassword})
        if verificarcion_de_usuario:
            session["user"] = tuser
            return redirect(url_for("menu_principal"))
        else:
            return render_template("login.html")
    else: 
        return render_template("login.html")

#Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

#Configuracion de Fabrica
@app.route("/conf_fabrica")
def conf_fabrica():
    if verificar_permiso():
        data = db.conf_fabrica.find_one()
        return render_template("conf_fabrica.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/conf_fabrica/aux", methods = ["POST"])
def conf_fabrica_aux():
    nombre_fabrica = request.form["nombre_fabrica"]
    tiempo_produccion = request.form["tiempo_produccion"]
    id = request.form["id"]
    db.conf_fabrica.update({"_id":ObjectId(id)},{"$set":{"nombre_fabrica":nombre_fabrica, "tiempo_produccion":tiempo_produccion}})
    return redirect(url_for("conf_fabrica"))

#Main Menu
@app.route("/menu_principal", methods=["POST","GET"])
def menu_principal():
    if verificar_permiso():
        return render_template("menu_principal.html")
    else:
        return redirect(url_for("login"))
#Modelos
@app.route("/modelos")
def modelos():
    if verificar_permiso():
        data = db.modelos.find()
        return render_template("modelos.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/modelos/<modelo>")
def agregar(modelo):
    if verificar_permiso():
        if modelo == "agregar":
            return render_template("modelo_agregar.html")
        else:
            data_modelo = db.modelos.find({"_id":ObjectId(modelo)})
            return render_template("modelo_editar.html", data = data_modelo)
    else:
        return redirect(url_for("login"))

@app.route("/modelos/agregar/aux", methods=["POST"])
def modelo_agregar_aux():
    tipo = request.form["tipo"]
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    memoria = request.form["memoria"]
    almacenamiento = request.form["almacenamiento"]
    procesador = request.form["procesador"]
    cores = request.form["cores"]
    resolucion = request.form["resolucion"]
    bandas = request.form["bandas"]
    precio = request.form["precio"]

    mod = {"tipo":tipo, "marca":marca, "modelo":modelo,
        "memoria":memoria, "almacenamiento":almacenamiento, "procesador":procesador, 
        "cores":cores, "resolucion":resolucion, "bandas":bandas, 
        "precio":precio}

    res = db.modelos.insert_one(mod)

    return redirect(url_for("modelos"))

@app.route("/modelos/editar/aux", methods=["POST"])
def modelo_editar_aux():
    tipo = request.form["tipo"]
    marca = request.form["marca"]
    modelo = request.form["modelo"]
    memoria = request.form["memoria"]
    almacenamiento = request.form["almacenamiento"]
    procesador = request.form["procesador"]
    cores = request.form["cores"]
    resolucion = request.form["resolucion"]
    bandas = request.form["bandas"]
    precio = request.form["precio"]

    mod = {"tipo":tipo,"marca":marca, "modelo":modelo, "memoria":memoria, "almacenamiento":almacenamiento, "procesador":procesador, 
        "cores":cores, "resolucion":resolucion, "bandas":bandas, 
        "precio":precio}

    res = db.modelos.update({"marca":marca, "modelo":modelo},mod)

    return redirect(url_for("modelos"))

@app.route("/modelos/eliminar/<modelo>")
def modelo_eliminar(modelo):
    mod = {"_id":ObjectId(modelo)}

    res = db.modelos.delete_one(mod)

    return redirect(url_for("modelos"))

#Clientes
@app.route("/clientes")
def clientes():
    if verificar_permiso():
        data = db.clientes.find()
        return render_template("clientes.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/clientes/<cliente>")
def cliente_agregar(cliente):
    if verificar_permiso():
        if cliente == "agregar":
            return render_template("cliente_agregar.html")
        else:
            data_modelo = db.clientes.find_one({"_id": ObjectId(cliente)})
            return render_template("cliente_editar.html", data = data_modelo)
    else:
        return redirect(url_for("login"))

@app.route("/clientes/agregar/aux", methods=["POST"])
def clientes_agregar_aux():
    nombre = request.form["nombre"]
    password = request.form["password"]
    tiempo_envio = request.form["tiempo_envio"]
    url = request.form["url"]

    cliente = {"nombre":nombre, "password":password, "tiempo_envio":tiempo_envio, "url":url}

    res = db.clientes.insert_one(cliente)

    return redirect(url_for("clientes"))

@app.route("/clientes/editar/aux", methods=["POST"])
def clientes_editar_aux():
    id = request.form["id"]
    nombre = request.form["nombre"]
    password = request.form["password"]
    tiempo_envio = request.form["tiempo_envio"]
    url = request.form["url"]

    cliente = {"nombre":nombre, "password":password, "tiempo_envio":tiempo_envio, "url":url}

    res = db.clientes.update({"_id":ObjectId(id)},cliente)

    return redirect(url_for("clientes"))

@app.route("/clientes/eliminar/<cliente>")
def cliente_eliminar(cliente):
    cli = {"_id":ObjectId(cliente)}

    res = db.clientes.delete_one(cli)

    return redirect(url_for("clientes"))

#Usuarios
@app.route("/usuarios")
def usuarios():
    if verificar_permiso():
        data = db.usuarios.find()
        return render_template("usuarios.html", data = data)
    else:
        return redirect(url_for("login"))


@app.route("/usuarios/<usuario>")
def usuarios_agregar(usuario):
    if verificar_permiso():
        if usuario == "agregar":
            return render_template("usuarios_agregar.html")
        else:
            data_modelo = db.usuarios.find_one({"_id": ObjectId(usuario)})
            return render_template("usuarios_editar.html", data = data_modelo)
    else:
        return redirect(url_for("login"))

@app.route("/usuarios/agregar/aux", methods=["POST"])
def usuarios_agregar_aux():
    usuario = request.form["usuario"]
    password = request.form["password"]

    usuario = {"usuario":usuario, "password":password}

    res = db.usuarios.insert_one(usuario)

    return redirect(url_for("usuarios"))

@app.route("/usuarios/editar/aux", methods=["POST"])
def usuarios_editar_aux():
    id = request.form["id"]
    usuario = request.form["usuario"]
    password = request.form["password"]

    us = {"usuario":usuario, "password":password}

    res = db.usuarios.update({"_id":ObjectId(id)},us)

    return redirect(url_for("usuarios"))

@app.route("/usuarios/eliminar/<usuario>")
def usuarios_eliminar(usuario):
    us = {"_id":ObjectId(usuario)}

    res = db.usuarios.delete_one(us)

    return redirect(url_for("usuarios"))

#Ordenes
@app.route("/ordenes")
def ordenes():
    if verificar_permiso():
        data = db.ordenes.find().sort('fecha_ingreso',-1)
        return render_template("ordenes.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/ordenes/<orden>")
def ordenes_editar(orden):
    if verificar_permiso():
        data_orden = db.ordenes.find_one({"_id" : ObjectId(orden)})
        data_terminales = db.modelos.aggregate([{"$lookup":{"from":"ordenes_terminales", "localField": "modelo", "foreignField":"modelo", "as":"modelo_temp"}},
                                                {"$unwind":"$modelo_temp"}])
        return render_template("ordenes_editar.html", data_orden = data_orden, data_terminales = data_terminales)
    else:
        return redirect(url_for("login"))

@app.route("/ordenes/terminales/<orden>")
def lista_terminales(orden):
    if verificar_permiso():
        data = db.ordenes_terminales.find({"orden":orden})
        return render_template("ordenes_terminales.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/ordenes/agregar/<orden>")
def ordenes_agregar(orden):
    if verificar_permiso():
        data_orden = db.ordenes.find_one({"_id" : ObjectId(orden)})
        data_terminales = db.modelos.aggregate([{"$lookup":{"from":"ordenes_terminales", "localField": "modelo", "foreignField":"modelo", "as":"modelo_temp"}},
                                                {"$match":{"modelo_temp":[]}}])
        return render_template("ordenes_agregar.html", data_orden = data_orden, data_terminales = data_terminales)
    else:
        return redirect(url_for("login"))

@app.route("/ordenes/agregar/aux", methods = ["POST"])
def ordenes_agregar_aux():
    mods = []
    modelos = db.modelos.find()
    for modelo in modelos:
        str_temp = "cantidad_" + modelo["modelo"]
        try:
            mods.append([modelo["modelo"],request.form[str_temp]])
        except:
            print("No hay nada aqui")
    
    for modelo in mods:
        action_temp = "Se agregaron " + modelo[1] + " unidades del modelo " + modelo[0] + " Manualmente"
        db.log_ordenes.insert({"orden":request.form["id"], "usuario":session["user"], "accion":action_temp, "fecha": datetime.now()})
        db.ordenes_terminales.insert({"orden":request.form["id"], "modelo": modelo[0], "cantidad": modelo[1]})

    return (redirect(f"/ordenes/{request.form['id']}"))
    
@app.route("/ordenes/editar/aux", methods = ["POST"])
def ordenes_editar_aux():
    mods = []
    modelos = db.modelos.find()
    for modelo in modelos:
        str_temp = "cantidad_" + modelo["modelo"]
        try:
            mods.append([modelo["modelo"],request.form[str_temp]])
        except:
            print("No hay nada aqui")
    test = []
    for modelo in mods:
        if modelo[1] == '0':
            action_temp = "Se elimino el modelo " + modelo[0] + " de la orden"
            db.log_ordenes.insert({"orden":request.form["id"], "usuario":session["user"], "accion":action_temp, "fecha": datetime.now()})
            db.ordenes_terminales.delete_one({"orden":request.form["id"], "modelo":modelo[0]})
        else:
            modelo_temp = db.ordenes_terminales.find_one({"orden":request.form["id"], "modelo":modelo[0]})
            action_temp = "Se actualizo el modelo " + modelo[0] + " de " + modelo_temp['cantidad'] + " unidades a " + modelo[1] + " unidades"
            db.log_ordenes.insert({"orden":request.form["id"], "usuario":session["user"], "accion":action_temp, "fecha": datetime.now()})
            db.ordenes_terminales.update({"orden":request.form["id"], "modelo":modelo[0]},{"$set":{"cantidad":modelo[1]}})

    return (redirect(f"/ordenes/{request.form['id']}"))

@app.route("/ordenes/cancelar/<orden>")
def ordenes_cancelar(orden):
    db.log_ordenes.insert({"orden":orden, "usuario":session["user"], "accion":"cancelacion manual", "fecha": datetime.now()})
    db.ordenes.update({"_id":ObjectId(orden)},{"$set":{"estado":"cancelado"}})
    return redirect(url_for("ordenes"))

@app.route("/ordenes/estado/<orden>")
def ordenes_estado(orden):
    old = db.ordenes.find_one({"_id":ObjectId(orden)})
    if (old['estado'] == "recibida"):
        db.ordenes.update({"_id":ObjectId(orden)},{"$set":{"estado":"en produccion"}})
        return redirect(url_for("ordenes"))
    elif (old['estado'] == "en produccion"):
        db.ordenes.update({"_id":ObjectId(orden)},{"$set":{"estado":"enviada"}})
        notificar_envio(orden)
        return redirect(url_for("ordenes"))
    else:
        return redirect(url_for("ordenes"))
    

#Estadisticas
@app.route("/estadisticas")
def estadisticas():
    if verificar_permiso():
        clientes = db.clientes.find()
        for cliente in clientes:
            response = requests.get(str(cliente['url']) + "/api/ReporteVentas")
            data = json.loads(response.json())
            for venta in data:
                temp = db.reporte_ventas.find_one({"id_detalle":venta['iddetalle']})
                if (not temp):
                    db.reporte_ventas.insert_one({"id_detalle":venta['iddetalle'], "id_venta":venta['idventa'], "cliente":cliente['_id'], "modelo":venta['modelo'],"cantidad":int(venta['cantidad'])})
                else:
                    print("ya ingresado")
            
        datos = db.reporte_ventas.find()
        x, y = []
        c = 0
        for dato in datos:
            x[c] = dato['modelo']
            y[x[c]] += dato['cantidad']
            c += 1

        matplotlib.pyplot.bar(x, y,)
        matplotlib.pyplot.savefig('graf.png')

        return render_template("estadisticas.html")
    else:
        return redirect(url_for("login"))

#Logs
@app.route("/log_ordenes")
def log_ordenes():
    if verificar_permiso():
        data = db.log_ordenes.find().sort('fecha',pymongo.DESCENDING)
        return render_template("log_ordenes.html", data = data)
    else:
        return redirect(url_for("login"))

@app.route("/log_rest")
def log_rest():
    if verificar_permiso():
        data = db.log_rest.find().sort('fecha',pymongo.DESCENDING)
        return render_template("log_rest.html", data = data)
    else:
        return redirect(url_for("login"))

#WebService

@app.route("/solicitar_inventario", methods = ["POST"])
def solicitar_inventario():
    data = request.json
    resp = db.clientes.find_one({"_id":ObjectId(data['usuario']), "password":data['pass']})
    if(resp):
        catalogo = db.modelos.find()
        l = list(catalogo)
        d = dumps(l)
        return d
    else:
        ret = {"acceso":"negado"}
        return jsonify(ret)

@app.route("/nueva_orden", methods = ["POST"])
def nueva_orden():
    data = request.json
    resp = db.clientes.find_one({"_id":ObjectId(data['usuario']), "password":data['pass']})
    if(resp):
        temp_id = db.ordenes.insert_one({"cliente":data['usuario'], "nombre":resp['nombre'], "fecha_ingreso": datetime.now(), "estado":"recibida"})
        for modelo in data['orden']:
            db.ordenes_terminales.insert_one({"orden":str(temp_id.inserted_id),"modelo":modelo['modelo'], "cantidad":modelo['cantidad']})
    else:
        ret = {"acceso":"negado"}
        return jsonify(ret)
    
    db.log_rest.insert_one({"orden":str(temp_id.inserted_id),"cliente":resp['nombre'],"accion":"Ingreso orden mediante servicios REST","fecha": datetime.now()})
    ret = {"orden":str(temp_id.inserted_id)}
    return jsonify(ret)

@app.route("/cancelar_orden", methods = ["POST"])
def cancelar_orden():
    data = request.json
    resp = db.clientes.find_one({"_id":ObjectId(data['usuario']), "password":data['pass']})
    if(resp):
        if (db.ordenes.find_one({"_id":ObjectId(data['orden'])})['cliente'] == data['usuario']):
            db.ordenes.update({"_id":ObjectId(data['orden'])},{"$set":{"estado":"cancelado"}})
            db.log_rest.insert_one({"orden":data['orden'],"cliente":resp['nombre'],"accion":"Cancelacion de orden mediante servicios REST","fecha": datetime.now()})
            ret = {"orden":"cancelada"}
            return jsonify(ret)
    else:
        ret = {"acceso":"negado"}
        return jsonify(ret)

###########Inicia el servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)