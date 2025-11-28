from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import pymysql
app = Flask(__name__)
app.secret_key = "clave_super_secreta_nutrivida"
API_KEY = "6a7697ebd97f47709ec251c5b6a12c96"
usuarios = {}



conexion = pymysql.connect(
    host="localhost",
    user="root",         
    password="",         
    database="nutrivida",   
    cursorclass=pymysql.cursors.DictCursor
)


def login_requerido(func):
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def inicio():
    return render_template('index.html')




@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        peso = request.form.get('peso')
        altura = request.form.get('altura')
        actividad = request.form.get('actividad')
        objetivo = request.form.get('objetivo')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        alergias = ", ".join(request.form.getlist('alergias'))
        dieta = request.form.get('dieta')
        experiencia = request.form.get('experiencia')

        try:
            
            with conexion.cursor() as cursor:
                cursor.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
                existente = cursor.fetchone()

                if existente:
                    flash("Este correo ya está registrado.", "danger")
                    return redirect(url_for('registro'))

            
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO usuarios
                    (nombre, apellidos, edad, sexo, peso, altura, actividad, objetivo,
                     alergias, dieta, experiencia, email, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    nombre, apellidos, edad, sexo, peso, altura, actividad,
                    objetivo, alergias, dieta, experiencia, email, password
                ))
                conexion.commit()

            
            session['usuario'] = email
            return redirect(url_for('perfil'))

        except Exception as e:
            print("ERROR REGISTRO:", e)
            flash("Hubo un error al registrar.", "danger")

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')

        conexion = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='nutrivida',
            cursorclass=pymysql.cursors.DictCursor
        )

        with conexion:
            with conexion.cursor() as cursor:
                sql = "SELECT * FROM usuarios WHERE email=%s LIMIT 1"
                cursor.execute(sql, (email,))
                usuario = cursor.fetchone()

        if not usuario:
            flash("Este correo no está registrado.", "danger")
            return redirect(url_for('login'))

        if usuario['password'] != password:
            flash("La contraseña es incorrecta.", "danger")
            return redirect(url_for('login'))

        session['usuario'] = usuario['email']
        return redirect(url_for('perfil'))

    return render_template('login.html')


@app.route('/perfil')
@login_requerido
def perfil():
    email = session['usuario']
    usuario = usuarios.get(email)
    return render_template('perfil.html', usuario=usuario)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))



@app.route('/alimentos')
def alimentos():
    return render_template('alimentos.html')


@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


@app.route('/calc_imc', methods=['GET', 'POST'])

def calc_imc():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura']) / 100
        imc = round(peso / (altura * altura), 2)
        resultado = imc

        if imc < 18.5:
            estado = "bajo"
            mensaje = "Estás por debajo del peso recomendado."
        elif 18.5 <= imc <= 24.9:
            estado = "normal"
            mensaje = "¡Felicidades! Estás en un peso saludable."
        elif 25 <= imc <= 29.9:
            estado = "sobrepeso"
            mensaje = "Tu IMC indica sobrepeso."
        else:
            estado = "obesidad"
            mensaje = "Tu IMC indica obesidad."

    return render_template('calc_imc.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calc_tmb', methods=['GET', 'POST'])

def calc_tmb():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        edad = int(request.form['edad'])
        sexo = request.form['sexo']

        if sexo == "masculino":
            tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
        else:
            tmb = 10 * peso + 6.25 * altura - 5 * edad - 161

        resultado = round(tmb, 2)

        if resultado < 1200:
            estado = "bajo"
            mensaje = "Tu TMB es baja."
        elif 1200 <= resultado <= 1800:
            estado = "normal"
            mensaje = "Tu TMB es normal."
        else:
            estado = "alto"
            mensaje = "Tu TMB es alta."

    return render_template('calc_tmb.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calc_gct', methods=['GET', 'POST'])

def calc_gct():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        tmb = float(request.form['tmb'])
        actividad = request.form['actividad']

        factores = {
            'sedentario': 1.2,
            'ligero': 1.375,
            'moderado': 1.55,
            'intenso': 1.725,
            'muy_intenso': 1.9
        }

        factor = factores.get(actividad, 1.2)
        gct = tmb * factor
        resultado = round(gct, 2)

        if gct < 1800:
            estado = "bajo"
            mensaje = "GCT bajo."
        elif 1800 <= gct <= 2800:
            estado = "normal"
            mensaje = "GCT normal."
        else:
            estado = "alto"
            mensaje = "GCT alto."

    return render_template('calc_gct.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calc_peso_ideal', methods=['GET', 'POST'])

def calc_peso_ideal():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        altura = float(request.form['altura']) / 100
        sexo = request.form['sexo']

        peso_ideal = 22 * (altura ** 2) if sexo == "masculino" else 21 * (altura ** 2)

        resultado = round(peso_ideal, 2)
        mensaje = f"Tu peso ideal es {resultado} kg."
        estado = "normal"

    return render_template('calc_peso_ideal.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calc_macros', methods=['GET', 'POST'])
@login_requerido
def calc_macros():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        calorias = float(request.form['calorias'])
        proteinas = round(calorias * 0.3 / 4, 2)
        grasas = round(calorias * 0.25 / 9, 2)
        carbohidratos = round(calorias * 0.45 / 4, 2)

        resultado = {
            "proteinas": proteinas,
            "grasas": grasas,
            "carbohidratos": carbohidratos
        }

        mensaje = "Distribución recomendada."
        estado = "normal"

    return render_template('calc_macros.html', resultado=resultado, estado=estado, mensaje=mensaje)



@app.route("/recetas", methods=["GET", "POST"])
def recetas():
    resultado = None
    mensaje = ""

    if request.method == "POST":
        texto = request.form["receta"]
        ingredientes = texto.strip().split("\n")

        API_KEY = "6a7697ebd97f47709ec251c5b6a12c96"

        total_cal = 0
        total_prot = 0
        total_fat = 0
        total_carb = 0
        detalle = []

        for ing in ingredientes:
           
            search_url = "https://api.spoonacular.com/food/ingredients/search"
            params = {"query": ing, "apiKey": API_KEY}

            search_res = requests.get(search_url, params=params).json()

            if not search_res.get("results"):
                mensaje = f"No pude reconocer: {ing}"
                continue

            ingredient_id = search_res["results"][0]["id"]

           
            info_url = f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/information"
            params = {"amount": 1, "apiKey": API_KEY}

            info_res = requests.get(info_url, params=params).json()

            nutri = info_res.get("nutrition", {}).get("nutrients", [])

            def get(n):
                for x in nutri:
                    if x["name"] == n:
                        return x["amount"]
                return 0

            cal = get("Calories")
            prot = get("Protein")
            fat = get("Fat")
            carb = get("Carbohydrates")

            total_cal += cal
            total_prot += prot
            total_fat += fat
            total_carb += carb

            detalle.append({
                "ingrediente": info_res.get("name", ing),
                "calorias": cal,
                "proteina": prot,
                "grasa": fat,
                "carbohidratos": carb
            })

        resultado = {
            "total": round(total_cal, 1),
            "prot": round(total_prot, 1),
            "fat": round(total_fat, 1),
            "carb": round(total_carb, 1),
            "detallado": detalle
        }

    return render_template("recetas.html", resultado=resultado, mensaje=mensaje)



if __name__ == '__main__':
    app.run(debug=True)
