import os
import logging
logging.basicConfig(level=logging.INFO)
LOG_LVL = logging.INFO
logger = logging.getLogger(__name__)

from flask import Flask, g, request, jsonify
from models import database, create_tables
from models import Bite, Apple
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World! This is Combine'


@app.route('/add', methods=["POST"])
def add_bite():
    table_name = request.values.get('table').strip()
    column = int(request.values.get('column'))
    slice = int(request.values.get('slice'))
    m = int(request.values.get('m'))
    tot = int(request.values.get('total'))  # total number of slices

    uploaded_file = request.files['file_slice']


    apples = Apple.select().where(Apple.table==table_name, Apple.column==column)
    if len(apples) == 0:
        logger.log(LOG_LVL, "\nNew apple: table=%s, columns=%d, slice=%d ,total=%d" % (table_name, column, slice, tot))
        apple = Apple(table=table_name, column=column, total=tot)
        apple.save()
    else:
        apple = apples[0]
        logger.log(LOG_LVL, "\nExisting apple: table=%s, columns=%d, slice=%d ,total=%d" % (table_name, column, slice, tot))

    b = Bite(apple=apple, slice=slice, m=m)
    b.save()
    fname = "%d-%s-%d-%d.json"
    uploaded_file.save(os.path.join('local_uploads', fname))
    b.fname = fname
    b.save()
    return jsonify({'msg': 'Bite: %d is added' % b.slice})


@app.route('/list', methods=["GET"])
def received():
    bites = """
    Bites
    <table>
        <tr>
            <td>Table</td>
            <td>Column</td>
            <td>Slice</td>
        </tr>
    """

    for bite in Bite.select():
        bites += "<tr>"
        bites += "<td>%s</td>\n" % bite.apple.table
        bites += "<td>%d</td>\n" % bite.apple.column
        bites += "<td>%d</td>\n" % bite.slice
        bites += "</tr>"
    bites += "</table>"
    return bites


@app.route('/status', methods=["GET"])
def status():
    apples = []
    for apple in Apple.select():
        slices = []
        for bite in apple.bites:
            slices.append(bite.slice)
        d = {"apple": apple.table}
        if sorted(slices) == range(apple.total):
            d["status"] = "complete"
        else:
            d["status"] = "missing"
        apples.append(d)
    return jsonify(apples=apples)


@app.route('/reason', methods=["GET"])
def reason():
    html = """
    <html><body>
    Apples
    <table>
    """
    for apple in Apple.select():
        slices = []
        for bite in apple.bites:
            slices.append(bite.slice)
        html += "<tr>"
        html += "<td>%s</td>" % apple.table
        html += "<td>%d</td>" % apple.column
        if sorted(slices) == range(apple.total):
            html += "<td> Completed </td>"
        else:
            html += "<td> Missing </td>"
        html += "</tr>"

    html += "</table></body></html>"

    return html


@app.before_request
def before_request():
    g.db = database
    g.db.connect(reuse_if_open=True)


@app.after_request
def after_request(response):
    g.db.close()
    return response


if __name__ == '__main__':
    create_tables()
    if 'port' in os.environ:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ['port']))
    else:
        app.run(debug=True, host='0.0.0.0')

