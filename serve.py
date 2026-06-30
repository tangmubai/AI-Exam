"""Small concurrent HTTP server for the offline practice site.

It binds to localhost because Cloudflare Tunnel is the public-facing process.
All user progress remains in each browser's localStorage.
"""

from __future__ import annotations

import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class PracticeHandler(SimpleHTTPRequestHandler):
    server_version = "AIPractice/1.0"

    def end_headers(self) -> None:
        if self.path.endswith((".html", ".js", ".css")) or self.path == "/":
            self.send_header("Cache-Control", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/_health":
            payload = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        # Friendly route for the mock-exam page.
        if self.path.split("?", 1)[0].rstrip("/") == "/practice":
            self.path = "/practice.html"
        super().do_GET()

    def list_directory(self, path: str):
        self.send_error(403, "Directory listing is disabled")
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args()

    os.chdir(ROOT)
    server = ThreadingHTTPServer((args.host, args.port), PracticeHandler)
    print(f"AI practice server: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
