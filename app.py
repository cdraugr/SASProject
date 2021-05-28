from flask import Flask, request, render_template, abort

from srcs.text_analytics import get_all_by_link
from srcs.utils import parse_links_from_json


app = Flask(__name__)


@app.route('/')
def my_form():
    links = parse_links_from_json('links.csv')
    return render_template('root.html', links=links)


@app.route('/', methods=['POST'])
def my_form_post():
    try:
        link = request.form['link']
        processed = get_all_by_link(link)
        return render_template('response.html', data=processed)
    except ValueError as e:
        abort(403, e)


@app.route('/parse-link', methods=['GET'])
def parse_link():
    try:
        link = request.args['link']
        processed = get_all_by_link(link)
        return render_template('response.html', data=processed)
    except ValueError as e:
        abort(403, e)
