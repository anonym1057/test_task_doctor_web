#!flask/bin/python
import json
import argparse

from flask import Flask, flash, request, redirect, url_for,send_from_directory

from file_manager import FileManager

app = Flask(__name__)

UPLOAD_FOLDER = '/store'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

file_manager=FileManager(UPLOAD_FOLDER)

@app.route("/storage", methods=['POST','GET','DELETE'])
def storage():
    """

    :return:
    """
    file_manager =app.config['FILE_MANAGER']
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return None

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return None

        hash_file=file_manager.upload(file)
        if hash_file:
            response = app.response_class(response={'hash': hash},
                                                  status=201,
                                                  mimetype='application/json')
            return redirect(url_for('uploaded_file',
                                    filename=hash_file))
        else:
            flash('Not created')
            return None

    elif request.method == 'GET':
        hash_file=request.args.get('hash')

        if hash_file:
            path=file_manager.download()
            if path:
                return send_from_directory(path)
        return None

    else: #method delete
        hash_file = request.args.get('hash')

        if hash_file:
            if file_manager.delete(hash_file):
                response = app.response_class(response='Deleted',
                                              status=200,
                                              mimetype='text/html')
            return response
        return None


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
    parser=init_parser()

    # получает аргументы
    args = parser.parse_args()

    app.config['FILE_MANAGER'] = FileManager(args.path_storage)

    app.run(debug=True,host=args.host,port=args.port)