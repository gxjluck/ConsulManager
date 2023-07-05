from flask import Blueprint
from flask_restful import reqparse, Resource, Api
import sys,traceback
sys.path.append("..")
from units import token_auth,selfkafka_manager
from werkzeug.datastructures import FileStorage
from units import upload
from units.config_log import *
blueprint = Blueprint('selfkafka',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('vendor',type=str)
parser.add_argument('account',type=str)
parser.add_argument('region',type=str)
parser.add_argument('group',type=str)
parser.add_argument('name',type=str)
parser.add_argument('ip',type=str)
parser.add_argument('port',type=str)
parser.add_argument('os',type=str)
parser.add_argument('del_dict',type=dict)
parser.add_argument('up_dict',type=dict)
parser.add_argument('file',type=FileStorage, location="files", help="File is wrong.")

class Upload(Resource):
    @token_auth.auth.login_required
    def post(self):
        file = parser.parse_args().get("file")
        try:
            return upload.read_execl(file.read(),'selfkafka')
        except Exception as e:
            logger.error(f"【selfkafka】导入失败,{e}\n{traceback.format_exc()}")
            return {"code": 50000, "data": f"导入失败！"}

class GetAllList(Resource):
    @token_auth.auth.login_required
    def get(self):
        args = parser.parse_args()
        return selfkafka_manager.get_all_list(args['vendor'],args['account'],args['region'],args['group'])

class selfkafkaApi(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self):
        logger.error('`````')
        return selfkafka_manager.get_service()
    def post(self):
        args = parser.parse_args()
        # args = {
        #     "account": "1",
        #     "group": "1",
        #     "ip": "127.0.0.1",
        #     "name": "1",
        #     "os": "linux",
        #     "port": "9092",
        #     "region": "1",
        #     "vendor": "1"
        # }
        logger.info(f'=======\n,{args}')
        return selfkafka_manager.add_service(args['vendor'],args['account'],args['region'],
                                            args['group'],args['name'],args['ip'],args['port'],args['os'])
    def put(self):
        args = parser.parse_args()
        del_dict = args['del_dict']
        up_dict = args['up_dict']
        resp_del = selfkafka_manager.del_service(del_dict['vendor'],del_dict['account'],
                                                del_dict['region'],del_dict['group'],del_dict['name'])
        resp_add = selfkafka_manager.add_service(up_dict['vendor'],up_dict['account'],up_dict['region'],
                                                up_dict['group'],up_dict['name'],up_dict['ip'],
                                                up_dict['port'],up_dict['os'])
        if resp_del["code"] == 20000 and resp_add["code"] == 20000:
            return {"code": 20000, "data": f"更新成功！"}
        else:
            return {"code": 50000, "data": f"更新失败！"}
    def delete(self):
        args = parser.parse_args()
        return selfkafka_manager.del_service(args['vendor'],args['account'],args['region'],args['group'],args['name'])

api.add_resource(GetAllList,'/api/selfkafka/alllist')
api.add_resource(selfkafkaApi, '/api/selfkafka/service')
api.add_resource(Upload,'/api/selfkafka/upload')
