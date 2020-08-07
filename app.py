from flask import Flask, redirect, url_for, render_template, request, jsonify
import os, time, json
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, static_url_path="", static_folder="static")

#client = MongoClient("mongodb://127.0.0.1:27017")
client = MongoClient("mongodb+srv://kevin:<passwd>@cluster0.vrnts.mongodb.net/filestorage?retryWrites=true&w=majority")


db = client.mongodb
filestorage = db.filestorage



@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        file = request.files['inputFile']
        content = file.read()
        doc = {
            "filename": file.filename,
            "contents": content
        }
        filestorage.insert_one(doc)
        return f"Successfully uploaded {file.filename}"


@app.route('/files')
def show_files():
    f = filestorage.find()
    response = []
    for item in f:
        item['_id'] = str(item['_id'])
        item['contents'] = str(item['contents'])
        response.append(item)
    return json.dumps(response)


@app.route('/clear')
def remove_all_documents():
    filestorage.remove({})
    return "Deleted all files"


@app.route('/last2')
def get_last_2():
    filelist = []
    results = filestorage.find().sort('_id', -1).limit(2)
    for item in results:
        item['_id'] = str(item['_id'])
        item['contents'] = str(item['contents'])
        filelist.append(item)
    return json.dumps(filelist)


@app.route('/difflast2')
def diff_last_2():
    filelist = []
    file1 = open('tempfile1.txt', 'wb')
    file2 = open('tempfile2.txt', 'wb')
    results = filestorage.find().sort('_id', -1).limit(2)
    d1 = results[0]['contents']
    d2 = results[1]['contents']
    file1.write(d1)
    file2.write(d2)
    file1.close()
    file2.close()
    timestr = time.strftime('%Y%m%d-%H%M%S')
    os.system(f"vimdiff tempfile2.txt tempfile1.txt -c 'set diffopt+=context:120' -c 'let g:html_number_lines=1' -c 'let g:html_no_pre=1' -c TOhtml -c 'w! ./static/diff{timestr}.html' -c 'qa!'" )
    return redirect(url_for('static', filename=f'diff{timestr}.html'))


@app.route('/showall', methods=['GET'])
def showallrecords():
    f = filestorage.find()
    response = []
    for item in f:
        item['_id'] = str(item['_id'])
        item['contents'] = str(item['contents'])
        response.append(item)
    return render_template('files.html', data=response)


@app.route("/delete", methods=["POST"])
def deleteone():
    id = request.form.get("item")
    filestorage.delete_one({'_id': ObjectId(id)})
    resp = jsonify('File deleted successfully!')
    resp.status_code = 200
    return resp


@app.route('/delete/<id>', methods=['GET', ])
def delete(id):
    filestorage.delete_one({'_id': ObjectId(id)})
    resp = jsonify('File deleted successfully!')
    resp.status_code = 200
    return resp


if __name__ == '__main__':
    app.run()
