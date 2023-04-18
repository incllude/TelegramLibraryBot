import os

from flask import Flask, send_file, after_this_request
from database import *
import pandas

app = Flask(__name__)
local = 'http://127.0.0.1:8080'
db = DatabaseConnector()

@app.route("/download/<book_id>", methods=['GET'])
def get_customers_show(book_id):

    ans = [x[1:] for x in db.get_stat({'book_id': book_id})]
    dict = {}
    dict['title'] = {i: j[0] for i, j in enumerate(ans)}
    dict['author'] = {i: j[1] for i, j in enumerate(ans)}
    dict['published'] = {i: j[2] for i, j in enumerate(ans)}
    dict['date_start'] = {i: j[3] for i, j in enumerate(ans)}
    dict['date_end'] ={i: j[4] for i, j in enumerate(ans)}
    df = pandas.DataFrame(dict)
    df.to_excel(f"data_book_{book_id}.xlsx")
    print({i: j[0] for i, j in enumerate(ans)})

    @after_this_request
    def delete_dile(response):
        os.remove(f"data_book_{book_id}.xlsx")
        return response

    return send_file(f"data_book_{book_id}.xlsx")
