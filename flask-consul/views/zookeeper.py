from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('zookeeper',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_zookeeper_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobzookeeper_name',type=str)
parser.add_argument('checked',type=str)

class zookeeper(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobzookeeper':
            jobzookeeper = consul_kv.get_keys_list('ConsulManager/jobs')
            jobzookeeper_list = [i.split('/jobs/')[1] for i in jobzookeeper if '/zookeeper/' in i]
            return {'code': 20000,'jobzookeeper':jobzookeeper_list}
        elif stype == 'zookeeper_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/zookeeper/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'zookeeperrules':
            return gen_config.get_zookeeperrules()
        elif stype == 'cstzookeeperconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_zookeeper_config = consul_kv.get_value(f'ConsulManager/assets/sync_zookeeper_custom/{iid}')
            cst_zookeeper_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_zookeeper_config and cst_zookeeper_config['ip'] != '':
                cst_zookeeper_config['ipswitch'] = True
            if 'port' in cst_zookeeper_config and cst_zookeeper_config['port'] != '':
                cst_zookeeper_config['portswitch'] = True
            return {'code': 20000, 'cst_zookeeper': cst_zookeeper_config}
        elif stype == 'cstzookeeperlist':
            args = parser.parse_args()
            jobzookeeper_name = args['jobzookeeper_name']
            checked = args['checked']
            cst_zookeeper_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_zookeeper_custom/')
            cst_zookeeper_keylist = [k.split('/')[-1] for k,v in cst_zookeeper_dict.items() if v != {}]
            zookeeper_info = consul_kv.get_res_services(jobzookeeper_name)
            if checked == 'false':
                return zookeeper_info
            else:
                cst_zookeeper_list = [i for i in zookeeper_info['res_list'] if i['iid'] in cst_zookeeper_keylist]
                return {'code': 20000, 'res_list': cst_zookeeper_list}
                
    def post(self, stype):
        if stype == 'zookeeperpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.zookeeper_config(services_dict['jobzookeeper_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstzookeeper':
            args = parser.parse_args()
            cst_zookeeper_dict = args['cst_zookeeper_dict']
            consul_zookeeper_cst = {}
            iid = cst_zookeeper_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_zookeeper_dict['portswitch'] and cst_zookeeper_dict['port'] != '':
                    consul_zookeeper_cst['port'] = int(cst_zookeeper_dict['port'])
                    sid_dict['Port'] = consul_zookeeper_cst['port']
                if cst_zookeeper_dict['ipswitch'] and cst_zookeeper_dict['ip'] != '':
                    consul_zookeeper_cst['ip'] = cst_zookeeper_dict['ip']
                    sid_dict['Address'] = consul_zookeeper_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_zookeeper_custom/{iid}',consul_zookeeper_cst)
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

api.add_resource(zookeeper, '/api/zookeeper/<stype>')
