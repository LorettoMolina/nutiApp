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
        flash("Registro exitoso. ¡Bienvenido a NutriVida!", "success")
        return redirect(url_for('perfil'))

    return render_template('registro.html')


@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        flash("Inicia sesión o regístrate primero.", "warning")
        return redirect(url_for('registro'))

    email = session['usuario']
    usuario = usuarios.get(email)
    return render_template('perfil.html', usuario=usuario)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('inicio'))


@app.route('/alimentos')
def alimentos():
    return render_template('alimentos.html')


@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


if __name__ == '__main__':
    app.run(debug=True)
