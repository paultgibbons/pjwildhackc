from flask import send_from_directory, Flask, render_template, request, flash, session, url_for, redirect
import json
import jinja2
import wave
import contextlib
from collections import Counter
from hodclient import *
import os
from werkzeug import secure_filename


UPLOAD_FOLDER = '/recordings'
ALLOWED_EXTENSIONS = set(['wav', 'mp3'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
resp = ""

def haven(filename):
    hodClient = HODClient("a0daabb0-7b7f-4b9d-a8a7-6d4e75a50cf5")


    # callback function
    def asyncRequestCompleted(jobID, error):
        print 'async completed'

        if error != None:
            for err in error.errors:
                result = "Error code: %d \nReason: %s \nDetails: %s" % (err.error, err.reason, err.detail)
                print result
        else:
            print 'getting result'
            hodClient.GetJobResult(jobID, requestCompleted)

    # callback function
    def requestCompleted(response, error):
        print 'here'
        global resp
        print 'here2'
        if error != None:
            print 'fffff'

            for err in error.errors:
                resp += "Error code: %d \nReason: %s \nDetails: %s\n" % (err.error, err.reason, err.detail)
        else:
            print 'here3'

            texts = response["document"]

            for text in texts:
                print 'for'
                print text
                resp = text['content']
                #resp += text["content"]

            print 'wtf'
        print resp

    paramArr = {}
    paramArr["file"] = filename#"test.mp3"

    hodClient.PostRequest(paramArr, HODApps.RECOGNIZE_SPEECH, async=True, callback=asyncRequestCompleted)

    #print word_dict
    #wdjson = json.dumps(word_dict)
    #print wdjson
    #return wdjson#word_dict
    print 'resp', resp
    return resp

def getParams(transcribed, d):
    print transcribed

    parts = transcribed.split()

    #parts = [str(x) for x in parts]
    print parts

    fld = []
    val = []

    for word in parts:
        if len(word) < 15:
            val.append(len(word))

    c = Counter(parts)
    for k, v in c.iteritems():
        fld.append( {"text":k, "size":(v*20)} )

    res = {
        'WC':len(parts),
        'WPM':(len(parts)*60) / d,
        'Vocab':len(set(parts)),
        'values':val,
        'fl': fld,
        'text': transcribed
    }
    return res

def getDuration(filename):
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return(duration)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ph', methods=['POST'])
def ph():
    file = request.files['file']
    print 'why'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
    print 'hi'
    text = haven(filename)
    print 'haven text', text
    res = getParams(str(text), getDuration(filename))
    print 'res', res
    return render_template('index.html', params=res)

if __name__ == '__main__':
    app.run()