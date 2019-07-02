import sys
import json
from multiprocessing import Process
from time import sleep
import os
import logging
from flask import Flask, g, request, jsonify, send_from_directory, abort
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

    uploaded_file = request.files['graph']

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
        if app.testing:
            combine_graphs(apple.id)
        else:
            g.db.close()
            p = Process(target=combine_graphs, args=(apple.id,))
            p.start()
    return jsonify({"apple": apple.id, "bite": b.id})


@app.route('/status', methods=["GET"])
def status():
    apples = [{"apple": apple.table, "status": apple.status, "complete": apple.complete} for apple in Apple.select()]
    return jsonify(apples=apples)


@app.route('/list', methods=["GET"])
def all_apples():
    return jsonify(apples=[apple.json() for apple in Apple.select()])


@app.route('/list_bites', methods=["GET"])
def all_bites():
    return jsonify(bites=[b.json() for b in Bite.select()])


@app.route('/get_graph', methods=["GET"])
def get_graph():
    apple_id = request.values.get('id')
    #apple_id = int(apple_id)
    apples = Apple.select().where(Apple.id==apple_id)
    print("apples: ")
    print(apples)
    print("len: ")
    print(len(apples))
    if len(apples) == 1:
        apple = apples[0]
        fname = apple.fname
        if fname != "":
            return send_from_directory(UPLOAD_DIR, fname, as_attachment=True)
    abort(404)


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


if __name__ == '__main__':
    create_tables()
    if 'port' in os.environ:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ['port']))
    else:
        app.run(debug=True, host='0.0.0.0')

