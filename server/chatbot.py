import mimetypes
import os
from urllib.parse import urlparse
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from face import faceParser
from text import textParser, responseGenerator
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitago.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
requestParser = textParser(engine=db.engine)
imageParser = faceParser()


@app.route('/')
def hello():
    return 'Hello World'


@app.route('/whatsapp', methods=['GET', 'POST'])
def reply_whatsapp():
    num_media = int(request.values.get('NumMedia'))
    request_message = request.values.get('Body')
    sender = request.values.get('from')
    response = MessagingResponse()

    if not num_media:  #process non image
        try:
            transactions = requestParser.parseInput(request_message)
            for transaction in transactions:
                requestParser.addTransaction(transaction[0], transaction[1], transaction[2])
            response_message = responseGenerator.generateTransactionTable(transactions)
            response.message(response_message)  # generate success message
        except:
            response.message('Pesan anda tidak dikenali, coba lagi.')

    else:  #process image
        media_files = []
        for idx in range(num_media):
            media_url = request.values.get(f'MediaUrl{idx}')
            mime_type = request.values.get(f'MediaContentType{idx}')
            media_files.append((media_url, mime_type))

            req = requests.get(media_url)
            file_extension = mimetypes.guess_extension(mime_type)
            media_sid = os.path.basename(urlparse(media_url).path)
            file_path = f'received_images/{media_sid}{file_extension}'
            with open(file_path, 'wb') as f:
                f.write(req.content)
        try:
            person = imageParser.testFace(file_path)
            if person == None:
                response.message('Wajah anda tidak cocok, coba lagi.')
            else:
                response.message('Terima kasih {}, kamu sudah diabsen!'.format(person))
        except:
            response.message('Wajah tidak terdeteksi, coba lagi. ')
    return str(response)


if __name__ == '__main__':
    requestParser.addType('ayam geprek')
    requestParser.addType('ayam saos')

    requestParser.addKeyword(1, 'ayam geprek')
    requestParser.addKeyword(1, 'geprek')
    requestParser.addKeyword(1, 'ayam gprk')

    requestParser.addKeyword(2, 'ayam saos')
    requestParser.addKeyword(2, 'ayam bbq')
    requestParser.addKeyword(2, 'ayam blackpaper')
    requestParser.addKeyword(2, 'ayam blackpepper')
    app.run(debug=True)
