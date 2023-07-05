from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('rabbitmq',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_rabbitmq_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobrabbitmq_name',type=str)
parser.add_argument('checked',type=str)

class rabbitmq(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobrabbitmq':
            jobrabbitmq = consul_kv.get_keys_list('ConsulManager/jobs')
            jobrabbitmq_list = [i.split('/jobs/')[1] for i in jobrabbitmq if '/rabbitmq/' in i]
            return {'code': 20000,'jobrabbitmq':jobrabbitmq_list}
        elif stype == 'rabbitmq_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/rabbitmq/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'rabbitmqrules':
            return gen_config.get_rabbitmqrules()
        elif stype == 'cstrabbitmqconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_rabbitmq_config = consul_kv.get_value(f'ConsulManager/assets/sync_rabbitmq_custom/{iid}')
            cst_rabbitmq_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_rabbitmq_config and cst_rabbitmq_config['ip'] != '':
                cst_rabbitmq_config['ipswitch'] = True
            if 'port' in cst_rabbitmq_config and cst_rabbitmq_config['port'] != '':
                cst_rabbitmq_config['portswitch'] = True
            return {'code': 20000, 'cst_rabbitmq': cst_rabbitmq_config}
        elif stype == 'cstrabbitmqlist':
            args = parser.parse_args()
            jobrabbitmq_name = args['jobrabbitmq_name']
            checked = args['checked']
            cst_rabbitmq_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_rabbitmq_custom/')
            cst_rabbitmq_keylist = [k.split('/')[-1] for k,v in cst_rabbitmq_dict.items() if v != {}]
            rabbitmq_info = consul_kv.get_res_services(jobrabbitmq_name)
            if checked == 'false':
                return rabbitmq_info
            else:
                cst_rabbitmq_list = [i for i in rabbitmq_info['res_list'] if i['iid'] in cst_rabbitmq_keylist]
                return {'code': 20000, 'res_list': cst_rabbitmq_list}
                
    def post(self, stype):
        if stype == 'rabbitmqpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.rabbitmq_config(services_dict['jobrabbitmq_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstrabbitmq':
            args = parser.parse_args()
            cst_rabbitmq_dict = args['cst_rabbitmq_dict']
            consul_rabbitmq_cst = {}
            iid = cst_rabbitmq_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_rabbitmq_dict['portswitch'] and cst_rabbitmq_dict['port'] != '':
                    consul_rabbitmq_cst['port'] = int(cst_rabbitmq_dict['port'])
                    sid_dict['Port'] = consul_rabbitmq_cst['port']
                if cst_rabbitmq_dict['ipswitch'] and cst_rabbitmq_dict['ip'] != '':
                    consul_rabbitmq_cst['ip'] = cst_rabbitmq_dict['ip']
                    sid_dict['Address'] = consul_rabbitmq_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_rabbitmq_custom/{iid}',consul_rabbitmq_cst)
                del sid_dict['Weights']
                del sid_dict['ContentHash']
                del sid_dict['Datacenter']
                sid_dict['name'] = sid_dict.pop('Service')
                sid_dict['Meta']['instance'] = f"{sid_dict['Address']}:{sid_dict['Port']}"
                sid_dict["check"] = { "tcp": sid_dict['Meta']['instance'],"interval": "60s" }
                consul_svc.del_sid(iid)
                consul_svc.add_sid(sid_dict)
                return {'code': 20000, 'data': '自定义实例信息修改成功！'}
            except Exception as e:
                logger.error(f'{e}\n{traceback.format_exc()}')
                return {'code': 50000, "data": '提交自定义实例信息格式错误！'}

api.add_resource(rabbitmq, '/api/rabbitmq/<stype>')
