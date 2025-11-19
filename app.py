from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "clave_super_secreta_nutrivida"

usuarios = {}

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
        alergias = request.form.getlist('alergias')
        dieta = request.form.get('dieta')
        experiencia = request.form.get('experiencia')

        if email in usuarios:
            flash("Este correo ya está registrado.", "danger")
            return redirect(url_for('registro'))

        usuarios[email] = {
            "nombre": nombre,
            "apellidos": apellidos,
            "edad": edad,
            "sexo": sexo,
            "peso": peso,
            "altura": altura,
            "actividad": actividad,
            "objetivo": objetivo,
            "email": email,
            "password": password,
            "alergias": alergias,
            "dieta": dieta,
            "experiencia": experiencia
        }

        session['usuario'] = email
        return redirect(url_for('perfil'))

    return render_template('registro.html')

@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('registro'))

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


@app.route('/calculadora/imc', methods=['GET', 'POST'])
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

    return render_template('calculadoras/imc.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calculadora/tmb', methods=['GET', 'POST'])
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

        # Mensajes basados en rango arbitrario (puedes ajustar)
        if resultado < 1200:
            estado = "bajo"
            mensaje = "Tu tasa metabólica basal es baja."
        elif 1200 <= resultado <= 1800:
            estado = "normal"
            mensaje = "Tu tasa metabólica basal está en rango normal."
        else:
            estado = "alto"
            mensaje = "Tu tasa metabólica basal es alta."

    return render_template('calculadoras/tmb.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calculadora/gct', methods=['GET', 'POST'])
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
            mensaje = "Gasto calórico total bajo."
        elif 1800 <= gct <= 2800:
            estado = "normal"
            mensaje = "Gasto calórico total en rango saludable."
        else:
            estado = "alto"
            mensaje = "Gasto calórico total alto."

    return render_template('calculadoras/gct.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calculadora/peso_ideal', methods=['GET', 'POST'])
def calc_peso_ideal():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        altura = float(request.form['altura']) / 100
        sexo = request.form['sexo']

        if sexo == "masculino":
            peso_ideal = 22 * (altura ** 2)
        else:
            peso_ideal = 21 * (altura ** 2)

        resultado = round(peso_ideal, 2)
        mensaje = f"Tu peso corporal ideal estimado es {resultado} kg."
        estado = "normal"

    return render_template('calculadoras/peso_ideal.html', resultado=resultado, estado=estado, mensaje=mensaje)


@app.route('/calculadora/macronutrientes', methods=['GET', 'POST'])
def calc_macros():
    resultado = None
    estado = None
    mensaje = ""

    if request.method == 'POST':
        calorias = float(request.form['calorias'])
        proteinas = round(calorias * 0.3 / 4, 2)    # 30% proteínas, 4 cal/g
        grasas = round(calorias * 0.25 / 9, 2)      # 25% grasas, 9 cal/g
        carbohidratos = round(calorias * 0.45 / 4, 2) # 45% carbs, 4 cal/g

        resultado = {
            "proteinas": proteinas,
            "grasas": grasas,
            "carbohidratos": carbohidratos
        }

        mensaje = "Distribución recomendada de macronutrientes."
        estado = "normal"

    return render_template('calculadoras/macronutrientes.html', resultado=resultado, estado=estado, mensaje=mensaje)


if __name__ == '__main__':
    app.run(debug=True)