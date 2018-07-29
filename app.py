import os
import MySQLdb
import logging as log

from random import randint
from threading import Thread

from flask import Flask, render_template, request, send_from_directory, after_this_request, jsonify
from werkzeug.utils import secure_filename, redirect

from operation import compute_data, remove_files

UPLOAD_FOLDER = os.path.dirname(__file__) + "/input_files"
DOWNLOAD_FOLDER = os.path.dirname(__file__) + "/output_files"
ALLOWED_EXTENSIONS = list(['xls', 'xlsx', 'csv'])

app = Flask(__name__)
app.secret_key = "MyUniqueKey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = MySQLdb.connect("localhost", "root", "root", "alite")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_page(alert=None):
    return render_template("index.html", alert=alert)


@app.route('/download', methods=['GET', 'POST'])
def download_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            alert = 'No file part.'
            return upload_page(alert=alert)

        else:
            f = request.files['file']
            if f.filename == '':
                alert = 'No selected file.'
                return upload_page(alert=alert)

            elif f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                filename = str(randint(0, 1000)) + "_" + filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                try:
                    cur = db.cursor()
                    result = cur.execute("INSERT INTO `task_status` (`filename`, `output_file`, `status`) "
                                         "VALUES ('" + str(filename) + "', NULL, 'PROCESSING')")
                    db.commit()
                    cur.close()

                    if result > 0:

                        def cal_file():
                            status = compute_data(UPLOAD_FOLDER + "/" + filename, 'active')

                            if status is not None:
                                try:
                                    cur_ = db.cursor()
                                    result_ = cur_.execute("UPDATE `task_status` SET `status` = 'DONE', "
                                                           "`output_file` = '" + "output_" + str(status) +
                                                           "' WHERE `filename` = '" + str(filename) + "'")
                                    db.commit()
                                    cur_.close()

                                    if result_ > 0:
                                        log.debug("IN_SUCCESS")
                                    else:
                                        log.debug("No filename is there: " + str(filename))

                                except Exception as e_:
                                    log.error("Failed Sql operation. Error message: %s", e_)

                            else:
                                log.debug('Internal Error. OR Sheet name not matched.')

                        thread = Thread(target=cal_file)
                        thread.start()
                        return render_template("download.html", alert="load", filename_=None, i_filename=str(filename))

                    else:
                        log.debug("No filename is there: " + str(filename))
                        alert = 'Internal Error.'
                        return upload_page(alert=alert)

                except Exception as e:
                    log.error("Failed Sql operation. Error message: %s", e)
                    alert = 'Internal Error.'
                    return upload_page(alert=alert)

            else:
                alert = 'Not supported file format.'
                return upload_page(alert=alert)

    else:
        return redirect(request.url)


@app.route('/status', methods=['GET', 'POST'])
def check_status():
    try:
        filename = request.form['filename']
        cur = db.cursor()
        result = cur.execute("SELECT `status`, `output_file` FROM `task_status` "
                             "WHERE `filename` = '" + str(filename) + "'")

        if result > 0:
            data = cur.fetchone()
            status = data[0]
            output_file = data[1]
            cur.close()
            return jsonify({'status': str(status), 'filename': str(output_file)})

        else:
            log.debug("No filename is there: " + str(filename))
            return jsonify({'status': 'FAILED', 'filename': 'NULL'})

    except Exception as e:
        log.error("Failed Sql operation in check_status. Error message: %s", e)
        return jsonify({'status': 'FAILED', 'filename': 'NULL'})


@app.route('/files/<path:filename>', methods=['GET', 'POST'])
def files(filename):

    @after_this_request
    def delete_output_file(response):
        remove_files(DOWNLOAD_FOLDER + "/" + filename)
        return response

    return send_from_directory(directory=DOWNLOAD_FOLDER, filename=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
