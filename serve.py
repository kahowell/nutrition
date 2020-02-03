import argparse
from build import app

parser = argparse.ArgumentParser()
parser.add_argument('--host', help='hostname to serve from (default: 127.0.0.1)')
parser.add_argument('--port', '-p', help='port to serve from (default: 5000)')
args = parser.parse_args()
app.serve(host=args.host, port=args.port)
