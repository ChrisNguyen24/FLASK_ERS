from flask import Flask , render_template, request, jsonify
from flask_mysqldb import MySQL
import math

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'demo_flask'
mysql = MySQL(app)

dataset = []
uu_dataset = {}
ii_dataset = {}

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM rates')
    rates = cur.fetchall()
    for rate in rates:
        print(rate[1])
    return 'hello'

@app.route('/test')
def recommend():
    id = request.args.get('user_id')
    load_data()
    # result = list_predicts(str(id))
    return jsonify( {
        'data': id
} ), 201

def load_data():
    global dataset, uu_dataset, ii_dataset
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM rates')
    rates = cur.fetchall()
    dataset = []
    for rate in rates:
        print('userId',rate[1])
        print('itemId',rate[2])
        print('rating',rate[3])
        dataset.append([
            str(rate[1]),
            str(rate[2]),
            str(rate[3])
        ])
        uu_dataset.setdefault(str(rate[1]), {})
        uu_dataset[str(rate[1])].setdefault(str(rate[2]), float(str(rate[3])))
        ii_dataset.setdefault(str(rate[2]), {})
        ii_dataset[str(rate[2])].setdefault(str(rate[1]), float(str(rate[3])))
        # dataset.append([
        #     str(rate[4]),
        #     str(rate[3]),
        #     str(rate[1])
        # ])
        # uu_dataset.setdefault(str(rate[4]), {})
        # uu_dataset[str(rate[4])].setdefault(str(rate[3]), float(str(rate[1])))
        # ii_dataset.setdefault(str(rate[3]), {})
        # ii_dataset[str(rate[3])].setdefault(str(rate[4]), float(str(rate[1])))
