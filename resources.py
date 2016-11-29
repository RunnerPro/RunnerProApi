
from models import Record
from db import session

from flask_restful import reqparse
from flask_restful import abort
from flask_restful import Resource
from flask_restful import fields
from flask_restful import marshal_with

record_fields = {
    'id': fields.Integer,
    'data': fields.String,
    'uri': fields.Url('records', absolute=True),
}

parser = reqparse.RequestParser()
parser.add_argument('data', type=str)

class RecordResource(Resource):
    @marshal_with(record_fields)
    def get(self, id):
        record = session.query(Record).filter(Record.id == id).first()
        if not record:
            abort(404, message="Record {} doesn't exist".format(id))
        return record

    def delete(self, id):
        record = session.query(Record).filter(Record.id == id).first()
        if not record:
            abort(404, message="Record {} doesn't exist".format(id))
        session.delete(record)
        session.commit()
        return {}, 204

    @marshal_with(record_fields)
    def put(self, id):
        parsed_args = parser.parse_args()
        record = session.query(Record).filter(Record.id == id).first()
        record.data = parsed_args['data']
        session.add(record)
        session.commit()
        return record, 201


class RecordListResource(Resource):
    @marshal_with(record_fields)
    def get(self):
        records = session.query(Record).all()
        return records

    @marshal_with(record_fields)
    def post(self):
        parsed_args = parser.parse_args()
        record = Record(data = parsed_args['data'])
        print(record)
        session.add(record)
        session.commit()
        return record, 201
