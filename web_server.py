#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

from flask import Flask, render_template, flash, request, redirect, Markup
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.validators import DataRequired
import validators
from urllib.parse import urlparse
import requests


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'KEY'
BACKEND_ENDPOINT = 'http://backend/api/'


class MainForm(Form):
    url = TextField('URL:', validators=[DataRequired()])


def call_backend(method, url):
    return requests.post(BACKEND_ENDPOINT + method, data={'url': url}).text


def url_validator(url):

    url_parsed = urlparse(url)
    if url_parsed.scheme:
        if validators.url(url):
            return True
        else:
            return False
    else:
        return True


@app.route("/", methods=['GET', 'POST'])
def index():
    form = MainForm(request.form)

    if request.method == 'POST':
        url = request.form['url']
        if form.validate():
            if url_validator(url):
                url_short = call_backend('generate', url)
                text = 'Generated <a href="{}" class="alert-link">{}</a>'.format(url_short, url_short)
                flash(Markup(text))
            else:
                flash('Error: URL is not valid')
        else:
            flash('Error: All the form fields are required.')

    return render_template('index.html', form=form)


@app.route('/r/<path>', methods=['GET'])
def foo(path):

    result = call_backend('check', path)
    #return result
    if result.strip():
        return redirect(result)
    else:
        return 'Not found'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run(host='0.0.0.0', port=80)

