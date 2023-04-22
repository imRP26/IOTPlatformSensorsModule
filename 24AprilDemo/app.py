import config
from flask import render_template
from models import Node


app = config.connex_app
app.add_api(config.basedir / 'swagger.yml')


@app.route('/')
def home():
    config.db.create_all()
    nodes = Node.query.all()
    return render_template('home.html', nodes=nodes)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8048, debug=True)
