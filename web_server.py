#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.


import azure.cosmos.cosmos_client as cosmos_client
from flask import Flask,redirect
import os

app = Flask(__name__)

@app.route('/')
def default_page():
    return 'Default page of the URL cutter'

@app.route('/<path:path>')

def catch_all(path):
    endpoint = os.environ['COSMOS_HOST']
    key = os.environ['COSMOS_KEY']

    client = cosmos_client.CosmosClient(endpoint, {'masterKey': key})

    database_name = 'telegram-bot'
    container_name = 'urls'
    result = None

    query = 'SELECT r.url FROM ' + container_name + ' r WHERE r.url_short="' + path + '"'
    query_result = client.QueryItems("dbs/" + database_name + "/colls/" + container_name, query,
                                  {'enableCrossPartitionQuery': True})
    for item in query_result:
        result = item['url']

    if result is not None:
        return redirect(result, code=302)
    else:
        return 'Not found'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run(host='0.0.0.0', port=80)

