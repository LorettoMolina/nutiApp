from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/alimentos')
def alimentos():
    return render_template('alimentos.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

if __name__ == '__main__':
    app.run(debug=True)
