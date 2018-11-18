#!flask/bin/python
import json
import argparse
import os
import logging
import daemon

from flask import Flask, request, send_from_directory

from file_manager import FileManager
from db import DataBaseStorage

app = Flask(__name__)


@app.route("/storage", methods=['POST', 'GET', 'DELETE'])
def storage():
    """
    File Storage Request Handler
    :return:
    """
    file_manager = app.config['FILE_MANAGER']
    database = app.config['DATA_BASE']

    response_error_bad_request = app.response_class(status=400,
                                                    mimetype='application/json')

    response_success_created = app.response_class(status=201,
                                                  mimetype='application/json')

    response_error_not_found = app.response_class(status=404,
                                                  mimetype='application/json')

    response_success_deleted = app.response_class(status=200,
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

        if hash_file:
            database.insert(hash_file, file.filename)
            response_success_created.response = [json.dumps({'hash': hash_file})]
            return response_success_created

        response_error_bad_request.response = [json.dumps({'error': 'file exist'})]
        return response_error_bad_request

    elif request.method == 'GET':
        hash_file = request.args.get('hash')

        if hash_file:
            path, name = file_manager.download(hash_file)
            if path:
                name_file = database.get_name_file(hash_file)
                return send_from_directory(path, name, as_attachment=True, attachment_filename=name_file)
            else:
                response_error_not_found.response = [json.dumps({'error': 'file does not exist'})]
                return response_error_not_found

        response_error_bad_request.response = [json.dumps({'error': 'query has not hash'})]
        return response_error_bad_request

    else:  # method delete
        hash_file = request.args.get('hash')

        if hash_file:
            if file_manager.delete(hash_file):
                database.delete(hash_file)
                response_success_deleted.response = ['Deleted']
                return response_success_deleted
            else:
                response_error_not_found.response = [json.dumps({'error': 'file does not exist'})]
                return response_error_not_found

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
    app.config['DATA_BASE'] = DataBaseStorage(os.path.join(args.path_storage, 'instance'), 'storage')
    logging.basicConfig(filename='storage.log', level=logging.DEBUG)

    with daemon.DaemonContext():
        app.run(host=args.host, port=args.port, debug=True)
