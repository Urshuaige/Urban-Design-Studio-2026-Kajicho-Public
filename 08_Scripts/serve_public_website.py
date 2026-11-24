#!/usr/bin/env python3
"""Serve the public Kajicho client on loopback with the hosted page routes."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class SiteHandler(SimpleHTTPRequestHandler):
    def translate_path(self, request_path):
        path = Path(super().translate_path(request_path))
        if not path.suffix and not path.is_file():
            page = path.with_suffix(".html")
            if page.is_file():
                return str(page)
        return str(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    website = Path(__file__).resolve().parents[1] / "website"
    handler = partial(SiteHandler, directory=website)
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
