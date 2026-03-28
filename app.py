import os
from flask import Flask, render_template, request, redirect, jsonify, session, url_for
import sqlite3
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename

# Capa CORE (Reglas)
from Core.bloques_macro import BLOQUES

# Capa REPOSITORY (Base de Datos)
from repository.eventos_repo import (
    eliminar_bloque_db, 
    obtener_bloques_db, 
    guardar_eventos_raw_db, 
    obtener_bloque_detalle_db, 
    actualizar_bloque_completo_db, 
    insertar_bloque_completo_db,
    eliminar_multiples_bloques_db
)

# Capa SERVICES y OTROS
from services.investing_fetcher import obtener_eventos_semana
from database import inicializar_db, obtener_bloques, obtener_bloque
from services.analisis_macro import actualizar_analisis
from services.bloques_service import detectar_tipo_bloque
from services.motor_eventos import procesar_eventos_raw

# =====================================================
# CONFIGURACIÓN DE RUTAS Y BASE DE DATOS (NUEVO)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "macrolab.db")

# Inicialización de DB
inicializar_db()

app = Flask(__name__)
app.secret_key = 'macro_lab_2026_private'

# =====================================================
# CONFIGURACIÓN DE SUBIDAS (FOTOS DE PERFIL)
# =====================================================
CARPETA_SUBIDAS = os.path.join(BASE_DIR, 'static', 'uploads', 'perfiles')
if not os.path.exists(CARPETA_SUBIDAS):
    os.makedirs(CARPETA_SUBIDAS)

app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDAS
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # 2MB
EXTENSIONES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif'}

def archivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS

# =====================================================
# DICCIONARIO DE TRADUCCIONES
# =====================================================
TRADUCCIONES = {
    'español': {
        'titulo': 'MACROLAB ANALYTICS',
        'subtitulo': 'Terminal de alta precisión para el análisis de flujos macroeconómicos.',
        'boton': 'ACCESO TERMINAL TRADER',
        'hub': 'Neural Hub',
        'assets': 'Data Assets',
        'access': 'Acceso Privado',
        'back': 'SALIR A TERMINAL',
        'user_label': 'Usuario Operativo | ID',
        'pass_label': 'Clave de Encriptación | PW',
        'verify_btn': 'VERIFICAR ACCESO'
    },
    'english': {
        'titulo': 'MACROLAB ANALYTICS',
        'subtitulo': 'High-precision terminal for institutional macroeconomic analysis.',
        'boton': 'TRADER TERMINAL ACCESS',
        'hub': 'Neural Hub',
        'assets': 'Data Assets',
        'access': 'Private Access',
        'back': 'EXIT TO TERMINAL',
        'user_label': 'Operational User | ID',
        'pass_label': 'Encryption Key | PW',
        'verify_btn': 'VERIFY ACCESS'
    }, 
    'français': {
        'titulo': 'MACROLAB ANALYTICS',
        'subtitulo': 'Le laboratoire institutionnel pour le traitement des données macroéconomiques.',
        'boton': 'ACCÈS AU TERMINAL CLIENT',
        'hub': 'Hub Neural',
        'assets': 'Actifs de Données',
        'access': 'Accès Privé',
        'back': 'SORTIR AU TERMINAL',
        'user_label': 'Utilisateur Opérationnel | ID',
        'pass_label': 'Clé de Chiffrement | PW',
        'verify_btn': 'VÉRIFIER L\'ACCÈS'
    },
    'português': {
        'titulo': 'MACROLAB ANALYTICS',
        'subtitulo': 'O laboratório institucional para processamento de datos macroeconômicos.',
        'boton': 'ACESSO AO TERMINAL DO CLIENTE',
        'hub': 'Hub Neural',
        'assets': 'Ativos de Dados',
        'access': 'Acesso Privado',
        'back': 'SAIR PARA TERMINAL',
        'user_label': 'Usuário Operacional | ID',
        'pass_label': 'Chave de Criptografia | PW',
        'verify_btn': 'VERIFICAR ACESSO'
    }
}

# =====================================================
# SEGURIDAD Y CONFIGURACIÓN
# =====================================================

@app.before_request
def verificar_sesion():
    rutas_publicas = ['inicio', 'login', 'static', 'set_language']
    
    if 'set_language' in request.path:
        return

    if 'user_id' not in session and request.endpoint not in rutas_publicas:
        return redirect('/login')

@app.route('/set_language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('index'))

# =====================================================
# RUTAS DE ACCESO Y LANDING
# =====================================================

@app.route("/")
def inicio():
    idioma = session.get('language', 'español')
    textos_idioma = TRADUCCIONES.get(idioma, TRADUCCIONES['español'])
    
    if 'user_id' in session:
        return render_template("index.html") 
    
    return render_template("landing.html", textos=textos_idioma)

@app.route("/login", methods=["GET", "POST"])
def login():
    idioma = session.get('language', 'español')
    textos_idioma = TRADUCCIONES.get(idioma, TRADUCCIONES['español'])

    if request.method == "POST":
        user_input = request.form.get("username")
        pass_input = request.form.get("password")

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT id, username, nombre_completo, foto_perfil FROM usuarios WHERE username = ? AND password = ?", 
                       (user_input, pass_input))
        usuario = cursor.fetchone()

        if usuario:
            session['user_id'] = usuario[0]
            session['username'] = usuario[1]
            session['nombre'] = usuario[2]
            session['foto_perfil'] = usuario[3] or 'default_user.png'
            session['rango'] = 'TRADER'

            cursor.execute("UPDATE usuarios SET estado = 'Activo' WHERE id = ?", (usuario[0],))
            conexion.commit()
            conexion.close()
            return redirect("/")
        
        conexion.close()
        return render_template("login.html", 
                               error="Acceso denegado. Credenciales incorrectas.", 
                               textos=textos_idioma)

    return render_template("login.html", textos=textos_idioma)

@app.route("/logout")
def logout():
    user_id = session.get('user_id')
    if user_id:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET estado = 'Desconectado' WHERE id = ?", (user_id,))
        conexion.commit()
        conexion.close()
    
    session.clear()
    return redirect("/login")

# =====================================================
# GESTIÓN DE PERFIL
# =====================================================

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    user_id = session.get('user_id')
    msg = None
    
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre_completo")
        nuevo_username = request.form.get("username")
        file = request.files.get('foto')
        
        cursor.execute("UPDATE usuarios SET nombre_completo = ?, username = ? WHERE id = ?", 
                       (nuevo_nombre, nuevo_username, user_id))
        
        session['nombre'] = nuevo_nombre
        session['username'] = nuevo_username

        if file and file.filename != '' and archivo_permitido(file.filename):
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            cursor.execute("UPDATE usuarios SET foto_perfil = ? WHERE id = ?", (filename, user_id))
            session['foto_perfil'] = filename
            msg = "Perfil y foto actualizados."
        else:
            msg = "Perfil actualizado correctamente."
            
        conexion.commit()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    usuario_data = cursor.fetchone()
    conexion.close()
    
    return render_template("perfil.html", usuario=usuario_data, mensaje=msg)

# =====================================================
# GESTIÓN DE USUARIOS (ADMIN)
# =====================================================

@app.route("/admin/guardar_todo", methods=["POST"])
def admin_guardar_todo():
    if session.get('username') != 'pablo_giraldo':
        return redirect("/")
    
    ids = request.form.getlist("id[]")
    nombres = request.form.getlist("nombre[]")
    usernames = request.form.getlist("username[]")
    passwords = request.form.getlist("password[]")

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    for i in range(len(ids)):
        cursor.execute("""
            UPDATE usuarios 
            SET nombre_completo = ?, username = ?, password = ? 
            WHERE id = ?
        """, (nombres[i], usernames[i], passwords[i], ids[i]))
    
    conexion.commit()
    conexion.close()
    return redirect("/admin/usuarios")

@app.route("/admin/usuarios", methods=["GET", "POST"])
def gestionar_usuarios():
    if session.get('username') != 'pablo_giraldo':
        return redirect("/")

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    if request.method == "POST":
        nuevo_user = request.form.get("username")
        nuevo_pass = request.form.get("password")
        nuevo_nombre = request.form.get("nombre")
        
        cursor.execute("INSERT INTO usuarios (username, password, nombre_completo, estado, foto_perfil) VALUES (?, ?, ?, 'Desconectado', 'default_user.png')",
                       (nuevo_user, nuevo_pass, nuevo_nombre))
        conexion.commit()

    cursor.execute("SELECT id, username, password, nombre_completo, estado FROM usuarios")
    lista_usuarios = cursor.fetchall()
    conexion.close()
    
    return render_template("gestion_usuarios.html", usuarios=lista_usuarios)

@app.route("/admin/eliminar_usuario/<int:id>")
def eliminar_usuario(id):
    if session.get('username') != 'pablo_giraldo':
        return redirect("/")

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    return redirect("/admin/usuarios")

# =====================================================
# GESTIÓN DE BLOQUES
# =====================================================

@app.route("/macro-admin")
def macro_admin():
    return render_template("macro_admin.html")

@app.route("/bloques")
def bloques():
    user_id = session.get('user_id') 
    divisa = request.args.get("divisa")
    if divisa == "Todos" or not divisa: divisa = None

    tipo = request.args.get("tipo")
    if tipo == "Todos" or not tipo: tipo = None

    fecha_desde = request.args.get("fecha_desde") or None
    fecha_hasta = request.args.get("fecha_hasta") or None

    datos = obtener_bloques(divisa, tipo, fecha_desde, fecha_hasta, user_id=user_id)

    return render_template(
        "bloques.html",
        bloques=datos,
        filtro_divisa=divisa or "Todos",
        filtro_tipo=tipo or "Todos",
        filtro_desde=fecha_desde or "",
        filtro_hasta=fecha_hasta or ""
    )

@app.route("/actualizar-semana")
def actualizar_semana():
    try:
        user_id = session.get('user_id')
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")

        if not fecha_inicio or not fecha_fin:
            hoy = datetime.now(timezone.utc)
            lunes = hoy - timedelta(days=hoy.weekday())
            sabado = lunes + timedelta(days=5)
            fecha_inicio = lunes.strftime("%Y-%m-%d")
            fecha_fin = sabado.strftime("%Y-%m-%d")

        eventos = obtener_eventos_semana(fecha_inicio, fecha_fin)
        
        if not eventos:
            return jsonify({"status": "ok", "message": "No se encontraron eventos"})

        guardar_eventos_raw_db(eventos, user_id=user_id)
        procesar_eventos_raw(user_id=user_id)

        return jsonify({
            "status": "success", 
            "message": "Eventos actualizados correctamente"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    user_id = session.get('user_id')
    if request.method == "POST":
        datos_bloque = {
            "fecha": request.form["fecha"],
            "hora": request.form["hora"],
            "divisa": request.form["divisa"],
            "user_id": user_id 
        }

        nombres = request.form.getlist("nombre_evento")
        tipos_internos = request.form.getlist("tipo_interno")
        previsiones = request.form.getlist("prevision")
        anteriores = request.form.getlist("anterior")
        reales = request.form.getlist("real")

        lista_eventos = []
        for i in range(len(nombres)):
            lista_eventos.append({
                "nombre": nombres[i],
                "prevision": previsiones[i],
                "anterior": anteriores[i],
                "real": reales[i],
                "tipo": tipos_internos[i],
                "user_id": user_id 
            })

        tipo_detectado = detectar_tipo_bloque(nombres[0])
        bloque_id = insertar_bloque_completo_db(datos_bloque, lista_eventos, tipo_detectado, user_id=user_id)

        actualizar_analisis(bloque_id)
        return redirect("/bloques")

    return render_template("nuevo.html", BLOQUES=BLOQUES)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_bloque(id):
    user_id = session.get('user_id')
    if request.method == "POST":
        datos_bloque = {
            "fecha": request.form["fecha"],
            "hora": request.form["hora"],
            "divisa": request.form["divisa"]
        }

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM eventos WHERE bloque_id=? AND user_id=?", (id, user_id))
        ids_eventos = [fila[0] for fila in cursor.fetchall()]
        conexion.close()

        lista_eventos = []
        for eid in ids_eventos:
            lista_eventos.append({
                "id": eid,
                "nombre": request.form.get(f"nombre_{eid}"),
                "prevision": request.form.get(f"prevision_{eid}"),
                "anterior": request.form.get(f"anterior_{eid}"),
                "real": request.form.get(f"real_{eid}"),
                "tipo": request.form.get(f"tipo_{eid}")
            })

        actualizar_bloque_completo_db(id, datos_bloque, lista_eventos, user_id=user_id)
        actualizar_analisis(id)
        return redirect("/bloques")

    bloque, eventos = obtener_bloque_detalle_db(id, user_id=user_id)
    return render_template("editar.html", bloque=bloque, eventos=eventos)

@app.route("/eliminar/<int:id>")
def eliminar_bloque(id):
    user_id = session.get('user_id')
    eliminar_bloque_db(id, user_id=user_id)
    return redirect("/bloques")

@app.route("/eliminar-multiples", methods=["POST"])
def eliminar_multiples():
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        ids = data.get('ids', [])
        if not ids:
            return jsonify({"status": "error", "message": "No seleccionados"}), 400
        
        eliminar_multiples_bloques_db(ids, user_id=user_id)
        return jsonify({"status": "success", "message": f"{len(ids)} eliminados"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/bloque/<int:id>")
def ver_bloque(id):
    user_id = session.get('user_id')
    bloque, eventos = obtener_bloque_detalle_db(id, user_id=user_id)
    
    if not bloque: return redirect("/bloques")

    mapa = {
        "USD": "OANDA:USDJPY", "EUR": "OANDA:EURUSD", "CAD": "OANDA:USDCAD",
        "GBP": "OANDA:GBPUSD", "AUD": "OANDA:AUDUSD", "JPY": "OANDA:USDJPY"
    }
    simbolo_tv = mapa.get(bloque[3], "OANDA:EURUSD")
    return render_template("detalle_bloque.html", bloque=bloque, eventos=eventos, simbolo_tv=simbolo_tv)

@app.route("/eliminar_evento/<int:evento_id>/<int:bloque_id>")
def eliminar_evento(evento_id, bloque_id):
    user_id = session.get('user_id')
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM eventos WHERE id=? AND user_id=?", (evento_id, user_id))
    conexion.commit()
    conexion.close()
    actualizar_analisis(bloque_id)
    return redirect(f"/editar/{bloque_id}")

from Library.biblioteca import registrar_biblioteca
registrar_biblioteca(app)

if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto, debug=True)