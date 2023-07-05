from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('kafka',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_kafka_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobkafka_name',type=str)
parser.add_argument('checked',type=str)

class kafka(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobkafka':
            jobkafka = consul_kv.get_keys_list('ConsulManager/jobs')
            jobkafka_list = [i.split('/jobs/')[1] for i in jobkafka if '/kafka/' in i]
            return {'code': 20000,'jobkafka':jobkafka_list}
        elif stype == 'kafka_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/kafka/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'kafkarules':
            return gen_config.get_kafkarules()
        elif stype == 'cstkafkaconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_kafka_config = consul_kv.get_value(f'ConsulManager/assets/sync_kafka_custom/{iid}')
            cst_kafka_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_kafka_config and cst_kafka_config['ip'] != '':
                cst_kafka_config['ipswitch'] = True
            if 'port' in cst_kafka_config and cst_kafka_config['port'] != '':
                cst_kafka_config['portswitch'] = True
            return {'code': 20000, 'cst_kafka': cst_kafka_config}
        elif stype == 'cstkafkalist':
            args = parser.parse_args()
            jobkafka_name = args['jobkafka_name']
            checked = args['checked']
            cst_kafka_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_kafka_custom/')
            cst_kafka_keylist = [k.split('/')[-1] for k,v in cst_kafka_dict.items() if v != {}]
            kafka_info = consul_kv.get_res_services(jobkafka_name)
            if checked == 'false':
                return kafka_info
            else:
                cst_kafka_list = [i for i in kafka_info['res_list'] if i['iid'] in cst_kafka_keylist]
                return {'code': 20000, 'res_list': cst_kafka_list}
                
    def post(self, stype):
        if stype == 'kafkapconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.kafka_config(services_dict['jobkafka_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstkafka':
            args = parser.parse_args()
            cst_kafka_dict = args['cst_kafka_dict']
            consul_kafka_cst = {}
            iid = cst_kafka_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_kafka_dict['portswitch'] and cst_kafka_dict['port'] != '':
                    consul_kafka_cst['port'] = int(cst_kafka_dict['port'])
                    sid_dict['Port'] = consul_kafka_cst['port']
                if cst_kafka_dict['ipswitch'] and cst_kafka_dict['ip'] != '':
                    consul_kafka_cst['ip'] = cst_kafka_dict['ip']
                    sid_dict['Address'] = consul_kafka_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_kafka_custom/{iid}',consul_kafka_cst)
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

api.add_resource(kafka, '/api/kafka/<stype>')
