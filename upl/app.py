from flask import Flask, render_template
import socketio
import asyncio
from web3 import Web3
from upl.main import UniswapPriceListener, W3

sio = socketio.Server(logger=True, async_mode=None)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = "very_secret_key!"


def update_pair_price(event):
    msg = Web3.toJSON(event)
    sio.emit(msg)
    print(msg)

async def listen_for_event(event_filter):
    while True:
        for event in event_filter.get_new_entries():
            update_pair_price(event)
        await asyncio.sleep(1)

def background_task():
    uni = UniswapPriceListener()
    uni.load_pairs()

    loop = asyncio.get_event_loop()
    tasks = []
    for pair in uni.pairs:
        event_filter = W3.eth.filter({"address": Web3.toChecksumAddress(pair.address)})    
        tasks.append(asyncio.create_task(listen_for_event(event_filter)))
    
    try:
        loop.run_until_complete(asyncio.gather(**tasks))
    finally:
        loop.close()


@app.route("/")
def index():
    sio.start_background_task(background_task)
    return render_template("index.html")