from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('memcached',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_memcached_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobmemcached_name',type=str)
parser.add_argument('checked',type=str)

class memcached(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobmemcached':
            jobmemcached = consul_kv.get_keys_list('ConsulManager/jobs')
            jobmemcached_list = [i.split('/jobs/')[1] for i in jobmemcached if '/memcached/' in i]
            return {'code': 20000,'jobmemcached':jobmemcached_list}
        elif stype == 'memcached_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/memcached/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'memcachedrules':
            return gen_config.get_memcachedrules()
        elif stype == 'cstmemcachedconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_memcached_config = consul_kv.get_value(f'ConsulManager/assets/sync_memcached_custom/{iid}')
            cst_memcached_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_memcached_config and cst_memcached_config['ip'] != '':
                cst_memcached_config['ipswitch'] = True
            if 'port' in cst_memcached_config and cst_memcached_config['port'] != '':
                cst_memcached_config['portswitch'] = True
            return {'code': 20000, 'cst_memcached': cst_memcached_config}
        elif stype == 'cstmemcachedlist':
            args = parser.parse_args()
            jobmemcached_name = args['jobmemcached_name']
            checked = args['checked']
            cst_memcached_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_memcached_custom/')
            cst_memcached_keylist = [k.split('/')[-1] for k,v in cst_memcached_dict.items() if v != {}]
            memcached_info = consul_kv.get_res_services(jobmemcached_name)
            if checked == 'false':
                return memcached_info
            else:
                cst_memcached_list = [i for i in memcached_info['res_list'] if i['iid'] in cst_memcached_keylist]
                return {'code': 20000, 'res_list': cst_memcached_list}
                
    def post(self, stype):
        if stype == 'memcachedpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.memcached_config(services_dict['jobmemcached_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstmemcached':
            args = parser.parse_args()
            cst_memcached_dict = args['cst_memcached_dict']
            consul_memcached_cst = {}
            iid = cst_memcached_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_memcached_dict['portswitch'] and cst_memcached_dict['port'] != '':
                    consul_memcached_cst['port'] = int(cst_memcached_dict['port'])
                    sid_dict['Port'] = consul_memcached_cst['port']
                if cst_memcached_dict['ipswitch'] and cst_memcached_dict['ip'] != '':
                    consul_memcached_cst['ip'] = cst_memcached_dict['ip']
                    sid_dict['Address'] = consul_memcached_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_memcached_custom/{iid}',consul_memcached_cst)
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

api.add_resource(memcached, '/api/memcached/<stype>')
