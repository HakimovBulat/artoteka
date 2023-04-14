from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('try.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(f'static/img/{uploaded_file.filename}')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')