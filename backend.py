#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.


import azure.cosmos.cosmos_client as cosmos_client
from flask import Flask, request
from urllib.parse import urlparse
import uuid
import os

cosmos = cosmos_client.CosmosClient(os.environ['COSMOS_HOST'], {'masterKey': os.environ['COSMOS_KEY']})

DOMAIN = 'http://example'

app = Flask(__name__)


@app.route('/api/check', methods=['POST'])
def check():

    url_short = request.form.to_dict()['url']
    database_name = 'telegram-bot'
    container_name = 'urls'
    url = ""

    query = 'SELECT r.url FROM ' + container_name + ' r WHERE r.url_short="' + url_short + '"'
    query_result = cosmos.QueryItems("dbs/" + database_name + "/colls/" + container_name, query,
                                         {'enableCrossPartitionQuery': True})
    for item in query_result:
        url = item['url']

    return url


@app.route('/api/generate', methods=['POST'])
def generate():

    url = request.form.to_dict()['url']
    url_parsed = urlparse(url)
    if not url_parsed.scheme:
        url = 'http://{}'.format(url)

    database_name = 'telegram-bot'
    container_name = 'urls'
    url_short = ""

    query = 'SELECT r.url_short FROM ' + container_name + ' r WHERE r.url="' + url + '"'
    query_result = cosmos.QueryItems("dbs/" + database_name + "/colls/" + container_name, query,
                                  {'enableCrossPartitionQuery': True})
    for item in query_result:
        url_short = item['url_short']

    if not url_short:
        url_short = '{}'.format(uuid.uuid4().hex.upper()[0:10])
        database_name = 'telegram-bot'
        container_name = 'urls'

        cosmos_data = {
            'id': 'IDIDIDID-234',
            'url': url,
            'url_short': url_short
        }
        cosmos.UpsertItem("dbs/" + database_name + "/colls/" + container_name, cosmos_data)

    return DOMAIN + url_short


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run(host='0.0.0.0', port=80)
