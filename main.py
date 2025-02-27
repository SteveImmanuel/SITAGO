import mimetypes
import os
import requests
import logging
import sys
import threading
import json
import datetime
from urllib.parse import urlparse
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from face import FaceParser
from text import TextParser
from record import Record
from responseGenerator import ResponseGenerator
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, Table, ForeignKey, DateTime
from queue import Queue
from connector import connector
from connector_util import ConnectorUtil

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s: %(message)s')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitago.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
requestParser = TextParser(engine=db.engine)
imageParser = FaceParser()
record = Record(engine=db.engine)

config = {}

with open('config.json') as json_file:
    config = json.load(json_file)

odoo_query = ConnectorUtil(config)
profile_queue = Queue()

order_global_id = 0


def daily_reset():
    global order_global_id
    order_global_id = odoo_query.insert_sale_order(datetime.datetime.now().isoformat())
    for i in range(config['employeeCount']):
        odoo_query.check_out(i)

@app.route('/')
def hello():
    return 'Hello World'


@app.route('/whatsapp', methods=['GET', 'POST'])
def reply_whatsapp():
    num_media = int(request.values.get('NumMedia'))
    request_message = request.values.get('Body')
    sender = request.values.get('From')
    response = MessagingResponse()

    if not num_media:  #process non image
        try:
            transactions = requestParser.parseInput(request_message)
            for transaction in transactions:
                print(transaction)
                record.addTransaction(sender, transaction[0], transaction[2])
                odoo_query.insert_sale_order_line(order_global_id, config['foodPrice'][transaction[1]], transaction[2],transaction[1])
            
            response_message = ResponseGenerator.generateTransactionTable(transactions)
            response.message(response_message)  # generate success message
        except Exception as e:
            print(e)
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

            if not record.calculateAndCheckHash(req.content):
                response.message('PERINGATAN!!! Anda menggunakan foto yang sama!')
                return str(response)

            with open(file_path, 'wb') as f:
                f.write(req.content)

        try:
            person = imageParser.testFace(file_path)
            if person == None:
                response.message('Wajah anda tidak cocok, coba lagi.')
            else:
                record.addPresence(sender)
                response.message('Terima kasih {}, kamu sudah diabsen!'.format(person))
                odoo_query.check_in(config['employee'][person])
        except:
            response.message('Wajah tidak terdeteksi, coba lagi. ')
    return str(response)


if __name__ == '__main__':
    metadata = MetaData()

    food_type = Table(
        'foodType',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String, nullable=False),
    )

    keyword = Table(
        'keyword',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('foodId', None, ForeignKey('foodType.id'), nullable=False),
        Column('keyword', String, nullable=False),
    )

    presence = Table(
        'presenceEmployee',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('sender', String(20), nullable=False),
        Column('time', DateTime, nullable=False),
    )

    image_hash = Table(
        'imageHash',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('hash', String(32), nullable=False),
    )

    transaction = Table(
        'storeTransaction',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('sender', String(20), nullable=False),
        Column('time', DateTime, nullable=False),
        Column('foodId', None, ForeignKey('foodType.id'), nullable=False),
        Column('amount', Integer, nullable=False),
    )

    metadata.create_all(db.engine)

    for idx, entry in enumerate(config['food']):
        requestParser.addType(entry)
        temp_keyword = config['food'][entry]
        for keyword in temp_keyword:
            requestParser.addKeyword(idx+1, keyword)

    threading.Thread(target=app.run).start()

    threading.Thread(target=connector, args=(profile_queue, config)).start()

    daily_reset()
    timer = threading.Timer(3600*24, daily_reset).start()

    while True:
        path, name = profile_queue.get()

        print('get new employee')
        imageParser.createFaceData(path, name)
