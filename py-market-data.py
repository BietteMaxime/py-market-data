#!/usr/bin/env python

from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.exceptions import WebSocketError
from gevent.pywsgi import WSGIServer
import gevent

from flask import Flask, jsonify, request, render_template, send_from_directory, session
import time, threading, random, os
import numpy


class market_data_server(Flask):
    def __init__(self, *args, **kwargs):
        super(market_data_server, self).__init__(*args, **kwargs)

        self.number_of_connexion = 0
        self.tickers_data = {'AAPL': {'value': 115.52, 'change': 0, 'rw': {'mean': 0, 'std': 0.1}}}


app = market_data_server(__name__)
app.debug = True
PORT = 5000
MIN_DELAY, MAX_DELAY = 1, 3


@app.route("/data/<ticker>", methods=['GET'])
def data(ticker):
    change = numpy.random.normal(app.tickers_data[ticker]['rw']['mean'], app.tickers_data[ticker]['rw']['std'])
    app.tickers_data[ticker]['value'] = app.tickers_data[ticker]['value'] + change
    app.tickers_data[ticker]['change'] += change
    info = {'ticker': ticker,
            'value': app.tickers_data[ticker]['value'],
            'change': app.tickers_data[ticker]['change'],
            }

    return jsonify(info)


@app.route("/updated")
def updated():
    """
    Notify the client that an update is ready. Contacted by the client to
    'subscribe' to the notification service.
    """
    ws = request.environ.get('wsgi.websocket', None)
    print("web socket retrieved")
    app.number_of_connexion += 1
    if ws:
        while True:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            gevent.sleep(delay)
            try:
                ws.send(str(app.number_of_connexion))
            except WebSocketError:
                print("socket died")
                app.number_of_connexion -= 1
                return "disconnected"
    else:
        raise RuntimeError("Environment lacks WSGI WebSocket support")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/page/<ticker_name>")
def ticker(ticker_name):
    return render_template("ticker.html", port=PORT, ticker=ticker_name)


if __name__ == "__main__":
    http_server = WSGIServer(('', PORT), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
    # app.run(port=port, debug=False)
