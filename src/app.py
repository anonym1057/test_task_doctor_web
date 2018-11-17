#!flask/bin/python
import json
import argparse
import logging
import daemon

from flask import Flask, request, send_from_directory

from src.file_manager import FileManager

app = Flask(__name__)

#logging.basicConfig(filename= 'log', level=logging.INFO)

@app.route("/storage", methods=['POST', 'GET', 'DELETE'])
def storage():
    """
    File Storage Request Handler
    :return:
    """
    file_manager = app.config['FILE_MANAGER']

    response_error_bad_request = app.response_class(status=400,
                                        mimetype='application/json')

    response_succses_created = app.response_class(status=201,
                                                  mimetype='application/json')

    response_error_not_found = app.response_class(status=404,
                                                    mimetype='application/json')

    response_succses_deleted = app.response_class(status=200,
                                                  mimetype='text/html')
    if request.method == 'POST':

        if 'file' not in request.files:
            response_error_bad_request.response = [json.dumps({'error': 'no from with keys file'})]
            return response_error_bad_request

        file = request.files['file']

        if file.filename == '':
            response_error_bad_request.response = [json.dumps({'error': 'key file has not value with file'})]
            return response_error_bad_request
        hash_file = file_manager.upload(file)
        logging.info("LAL")
        if hash_file:
            response_succses_created.response = [json.dumps({'hash': hash_file})]
            return response_succses_created
        else:
            response_error_bad_request.response = [json.dumps({'error': 'file exist'})]
            return response_error_bad_request

    elif request.method == 'GET':
        hash_file = request.args.get('hash')

        if hash_file:
            path,name = file_manager.download(hash_file)
            if path:
                print(path, name)
                return send_from_directory(path,name)
            else:
                response_error_not_found.response = [json.dumps({'error': 'file does not exist'})]
                return response_error_not_found

        response_error_bad_request.response = [json.dumps({'error': 'query has not hash'})]
        return response_error_bad_request

    else:  # method delete
        hash_file = request.args.get('hash')

        if hash_file:
            if file_manager.delete(hash_file):
                response_succses_deleted.response=['Deleted']
                return response_succses_deleted
            else:
                response_error_not_found.response = [json.dumps({'error': 'file does not exist'})]
                return response_error_not_found

        else:
            response_error_bad_request.response = [json.dumps({'error': 'query has not hash'})]
            return response_error_bad_request


def init_parser():
    """
    Init parser arguments
    :return: parser
    """
    parser = argparse.ArgumentParser(
        description='Service to access file storage')

    parser.add_argument(
        'path_storage',
        type=str,
        metavar="FILE",
        help="path to the folder where files are stored",
    )

    parser.add_argument(
        '-a',
        '--host',
        type=str,
        help="host service",
        default='127.0.0.1'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        help="port service",
        default='5000'
    )

    return parser


if __name__ == '__main__':
    parser = init_parser()

    # получает аргументы
    args = parser.parse_args()
    app.config['FILE_MANAGER'] = FileManager(args.path_storage)

    with daemon.DaemonContext():
        app.run(host=args.host, port=args.port)
