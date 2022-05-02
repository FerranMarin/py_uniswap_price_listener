import asyncio

import socketio
from flask import Flask, render_template
from flask_cors import CORS
from web3 import Web3

from main import W3, UniswapPriceListener

sio = socketio.Server(logger=True, async_mode=None)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = "very_secret_key!"
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app)

def update_pair_price(pair):
    old_price = pair.price
    current_price = pair.get_pair_price()
    if old_price != current_price:
        msg = f"New price for {pair.symbol}! [{old_price} -> {current_price}]"        
        sio.emit(msg)
        pair.price = current_price
    

async def listen_for_event(event_filter, pair):
    while True:
        for _ in event_filter.get_new_entries():
            update_pair_price(pair)
        await asyncio.sleep(1)

def background_task():
    uni = UniswapPriceListener()
    uni.load_pairs(sio)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for pair in uni.pairs:
        event_filter = W3.eth.filter({"address": Web3.toChecksumAddress(pair.address)})    
        try:
            loop.run_until_complete(listen_for_event(event_filter, pair))
        finally:
            loop.close()


@app.route("/")
def index():
    sio.start_background_task(background_task)
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
