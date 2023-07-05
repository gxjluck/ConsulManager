from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('flink',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_flink_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobflink_name',type=str)
parser.add_argument('checked',type=str)

class flink(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobflink':
            jobflink = consul_kv.get_keys_list('ConsulManager/jobs')
            jobflink_list = [i.split('/jobs/')[1] for i in jobflink if '/flink/' in i]
            return {'code': 20000,'jobflink':jobflink_list}
        elif stype == 'flink_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/flink/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'flinkrules':
            return gen_config.get_flinkrules()
        elif stype == 'cstflinkconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_flink_config = consul_kv.get_value(f'ConsulManager/assets/sync_flink_custom/{iid}')
            cst_flink_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_flink_config and cst_flink_config['ip'] != '':
                cst_flink_config['ipswitch'] = True
            if 'port' in cst_flink_config and cst_flink_config['port'] != '':
                cst_flink_config['portswitch'] = True
            return {'code': 20000, 'cst_flink': cst_flink_config}
        elif stype == 'cstflinklist':
            args = parser.parse_args()
            jobflink_name = args['jobflink_name']
            checked = args['checked']
            cst_flink_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_flink_custom/')
            cst_flink_keylist = [k.split('/')[-1] for k,v in cst_flink_dict.items() if v != {}]
            flink_info = consul_kv.get_res_services(jobflink_name)
            if checked == 'false':
                return flink_info
            else:
                cst_flink_list = [i for i in flink_info['res_list'] if i['iid'] in cst_flink_keylist]
                return {'code': 20000, 'res_list': cst_flink_list}
                
    def post(self, stype):
        if stype == 'flinkpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.flink_config(services_dict['jobflink_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstflink':
            args = parser.parse_args()
            cst_flink_dict = args['cst_flink_dict']
            consul_flink_cst = {}
            iid = cst_flink_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_flink_dict['portswitch'] and cst_flink_dict['port'] != '':
                    consul_flink_cst['port'] = int(cst_flink_dict['port'])
                    sid_dict['Port'] = consul_flink_cst['port']
                if cst_flink_dict['ipswitch'] and cst_flink_dict['ip'] != '':
                    consul_flink_cst['ip'] = cst_flink_dict['ip']
                    sid_dict['Address'] = consul_flink_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_flink_custom/{iid}',consul_flink_cst)
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

api.add_resource(flink, '/api/flink/<stype>')
