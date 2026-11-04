"""Serve the bundled demo on this machine only; standard-library Python 3."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import threading, webbrowser

if __name__ == '__main__':
    root=Path(__file__).resolve().parent/'dist'
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
    url=f'http://127.0.0.1:{server.server_port}/'
    print(f'Kajicho demo: {url}\nPress Ctrl+C to stop.',flush=True)
    threading.Timer(.5,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
