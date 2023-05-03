import config
from flask import render_template
from models import Node


app = config.connex_app
app.add_api(config.basedir / 'swagger.yml')
flask_app = app.app


@app.route('/')
def home():
    config.db.create_all()
    nodes = Node.query.all()
    return render_template('home.html', nodes=nodes)


@app.route('/stream')
def stream():
    def generate():
        with open('sensorManager.log') as f:
            while True:
                yield f.read()
                sleep(1)
    return flask_app.response_class(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8040, debug=True)
