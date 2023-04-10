import argparse
from aiohttp import web
from app import create_app


def main(args=None):
    parser = argparse.ArgumentParser(description='Run aiohttp server')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Server port')
    parser.add_argument('-H', '--host', default='localhost', help='Server host')
    parsed_args = parser.parse_args(args)

    app = create_app()
    web.run_app(app, host=parsed_args.host, port=parsed_args.port)


if __name__ == '__main__':
    main()
