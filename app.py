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


@app.route('/add', methods=["GET"])
def add_bite():
    table_name = request.args.get('table').strip()
    column = int(request.args.get('column'))
    slice = int(request.args.get('slice'))
    tot = int(request.args.get('total'))  # total number of slices

    apples = Apple.select().where(Apple.table==table_name, Apple.column==column)
    if len(apples) == 0:
        logger.log(LOG_LVL, "\nNew apple: table=%s, columns=%d, slice=%d ,total=%d" % (table_name, column, slice, tot))
        apple = Apple(table=table_name, column=column, total=tot)
        apple.save()
    else:
        apple = apples[0]
        logger.log(LOG_LVL, "\nExisting apple: table=%s, columns=%d, slice=%d ,total=%d" % (table_name, column, slice, tot))

    b = Bite(apple=apple, slice=slice)
    b.save()
    return 'Bite: %d is added' % b.slice


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

    # d = dict()
    # meta = dict()
    # for bite in Bite.select():
    #     if bite.table not in d:
    #         d[bite.table] = dict()
    #         meta[bite.table] = dict()
    #     if bite.column not in d[bite.table]:
    #         d[bite.table][bite.column] = []
    #         meta[bite.table][bite.column] = dict()
    #         meta[bite.table][bite.column]["total"] = bite.total
    #
    #     d[bite.table][bite.column].append(bite.slice)
    #
    # print("tables: "+str(d.keys()))
    # for table in d.keys():
    #     for col in d[table].keys():
    #         bites += "<tr>"
    #         bites += "<td>%s</td>\n" % table
    #         bites += "<td>%d</td>\n" % col
    #         print("table: "+str(table)+" col: "+str(col))
    #         print("range: "+str(range(max(d[table][col]))))
    #         print("sorted: "+str(sorted(d[table][col])))
    #         if range(max(d[table][col])+1) == sorted(d[table][col]):
    #             bites += "<td>Complete</td>\n"
    #         else:
    #             bites += "<td> Missing </td>\n"
    #
    #         bites += "</tr>"
    #
    # bites += "</table>"
    # return bites

# @app.route('/reason', methods=["GET"])
# def reason():
#     bites = """
#     Bites
#     <table>
#     """
#     d = dict()
#     meta = dict()
#     for bite in Bite.select():
#         if bite.table not in d:
#             d[bite.table] = dict()
#             meta[bite.table] = dict()
#         if bite.column not in d[bite.table]:
#             d[bite.table][bite.column] = []
#             meta[bite.table][bite.column] = dict()
#             meta[bite.table][bite.column]["total"] = bite.total
#
#         d[bite.table][bite.column].append(bite.slice)
#
#     print("tables: "+str(d.keys()))
#     for table in d.keys():
#         for col in d[table].keys():
#             bites += "<tr>"
#             bites += "<td>%s</td>\n" % table
#             bites += "<td>%d</td>\n" % col
#             print("table: "+str(table)+" col: "+str(col))
#             print("range: "+str(range(max(d[table][col]))))
#             print("sorted: "+str(sorted(d[table][col])))
#             if range(max(d[table][col])+1) == sorted(d[table][col]):
#                 bites += "<td>Complete</td>\n"
#             else:
#                 bites += "<td> Missing </td>\n"
#
#             bites += "</tr>"
#
#     bites += "</table>"
#     return bites


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


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

