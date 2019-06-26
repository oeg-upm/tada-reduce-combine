import sys
import json
from multiprocessing import Process
from time import sleep
import os
import logging
from flask import Flask, g, request, jsonify
from models import get_database, create_tables
from models import Bite, Apple
from models import STATUS_PROCESSING, STATUS_COMPLETE
logging.basicConfig(level=logging.INFO)
LOG_LVL = logging.INFO
logger = logging.getLogger(__name__)

app = Flask(__name__)
UPLOAD_DIR = 'local_uploads'


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

    if apple.complete:
        return jsonify(error="The apple is already complete, your request will not be processed"), 400

    b = Bite(apple=apple, slice=slice, m=m)
    b.save()
    fname = "%d-%s-%d-%d.json" % (b.id, b.apple.table.replace(" ", "_"), b.apple.column, b.slice)
    uploaded_file.save(os.path.join(UPLOAD_DIR, fname))
    b.fname = fname
    b.save()

    slices = []
    for bite in apple.bites:
        slices.append(bite.slice)
    if sorted(slices) == range(apple.total):
        apple.complete = True
        apple.save()

    if apple.complete:

        # combine_graphs(database, apple)
        g.db.close()
        p = Process(target=combine_graphs, args=(apple.id,))
        p.start()
    return jsonify({"apple": apple.id, "bite": b.id})


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
    # apples = []
    # for apple in Apple.select():
    #     slices = []
    #     for bite in apple.bites:
    #         slices.append(bite.slice)
    #     d = {"apple": apple.table}
    #     if sorted(slices) == range(apple.total):
    #         d["status"] = "complete"
    #     else:
    #         d["status"] = "missing"
    #     apples.append(d)
    # return jsonify(apples=apples)
    # apples = []
    # for apple in Apple.select(Apple.table, Apple.status, Apple.complete):
    #     d = {"apple": apple.table, "status": apple.status, "complete": apple.}
    #     if apple.complete:
    #         print("apple: %s, status: %s" % (apple.table, str(apple.complete)))
    #         d["status"] = "complete"
    #     else:
    #         d["status"] = "missing"
    #     apples.append(d)
    # return jsonify(apples=apples)
    # return jsonify(apples=Apple.select())
    apples = [{"apple": apple.table, "status": apple.status, "complete": apple.complete} for apple in Apple.select()]
    #return jsonify(apples=Apple.select(Apple.table, Apple.status, Apple.complete))
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
    g.db = get_database()
    g.db.connect(reuse_if_open=True)


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/process')
def multi_process():
    p = Process(target=f, args=('bob',))
    p.start()
    return jsonify(results=["Yes"])


def combine_graphs(apple_id):
    #create_tables()
    # database.connect(reuse_if_open=True)
    # apple = Apple.select().where(Apple.id==apple_id)[0]
    # create_tables()
    database = get_database()
    database.connect(reuse_if_open=True)
    apple = Apple.select().where(Apple.id==apple_id)[0]
    apple.status = STATUS_PROCESSING
    apple.save()
    graphs = []
    for bite in apple.bites:
        print("bite: %d" % bite.id)
        f = open(os.path.join(UPLOAD_DIR, bite.fname))
        j = json.load(f)
        graphs.append(j)
        f.close()
    graph = merge_graphs(graphs=graphs)
    fname = "%d-%s-%d-merged.json" % (apple.id, apple.table.replace(" ", "_"), apple.column)
    f = open(os.path.join(UPLOAD_DIR, fname), "w")
    f.write(json.dumps(graph))
    f.close()
    apple.fname = fname
    apple.status = STATUS_COMPLETE
    apple.save()
    database.close()


def merge_graphs(graphs):
    if len(graphs) == 1:
        return graphs[0]
    elif len(graphs) == []:
        return None
    else:
        graph = graphs[0]
        for g in graphs[1:]:
            for uri in g.keys():
                if uri in graph:
                    graph[uri]["Lc"] += g[uri]["Lc"]
                else:
                    graph[uri] = g[uri]
        return graph











def f(name):
    print('hello', name)
    for i in range(5):
        print("Hello")
        sleep(1)






if __name__ == '__main__':
    create_tables()
    if 'port' in os.environ:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ['port']))
    else:
        app.run(debug=True, host='0.0.0.0')

