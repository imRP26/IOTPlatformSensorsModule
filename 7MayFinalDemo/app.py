import config
from flask import render_template
from models import Node
import os
from time import sleep


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
    '''
    Generator Function that yields new lines in a file
    '''
    def generate():
        with open('sensorManager.log') as logfile:
            logfile.seek(0, os.SEEK_END)
            while True:
                line = logfile.readline()
                # sleep if file hasn't been updated
                if not line:
                    sleep(0.1)
                    continue
                yield line
    return flask_app.response_class(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8040, debug=True)
