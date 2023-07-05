from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('varnish',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_varnish_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobvarnish_name',type=str)
parser.add_argument('checked',type=str)

class varnish(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobvarnish':
            jobvarnish = consul_kv.get_keys_list('ConsulManager/jobs')
            jobvarnish_list = [i.split('/jobs/')[1] for i in jobvarnish if '/varnish/' in i]
            return {'code': 20000,'jobvarnish':jobvarnish_list}
        elif stype == 'varnish_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/varnish/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'varnishrules':
            return gen_config.get_varnishrules()
        elif stype == 'cstvarnishconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_varnish_config = consul_kv.get_value(f'ConsulManager/assets/sync_varnish_custom/{iid}')
            cst_varnish_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_varnish_config and cst_varnish_config['ip'] != '':
                cst_varnish_config['ipswitch'] = True
            if 'port' in cst_varnish_config and cst_varnish_config['port'] != '':
                cst_varnish_config['portswitch'] = True
            return {'code': 20000, 'cst_varnish': cst_varnish_config}
        elif stype == 'cstvarnishlist':
            args = parser.parse_args()
            jobvarnish_name = args['jobvarnish_name']
            checked = args['checked']
            cst_varnish_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_varnish_custom/')
            cst_varnish_keylist = [k.split('/')[-1] for k,v in cst_varnish_dict.items() if v != {}]
            varnish_info = consul_kv.get_res_services(jobvarnish_name)
            if checked == 'false':
                return varnish_info
            else:
                cst_varnish_list = [i for i in varnish_info['res_list'] if i['iid'] in cst_varnish_keylist]
                return {'code': 20000, 'res_list': cst_varnish_list}
                
    def post(self, stype):
        if stype == 'varnishpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.varnish_config(services_dict['jobvarnish_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstvarnish':
            args = parser.parse_args()
            cst_varnish_dict = args['cst_varnish_dict']
            consul_varnish_cst = {}
            iid = cst_varnish_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_varnish_dict['portswitch'] and cst_varnish_dict['port'] != '':
                    consul_varnish_cst['port'] = int(cst_varnish_dict['port'])
                    sid_dict['Port'] = consul_varnish_cst['port']
                if cst_varnish_dict['ipswitch'] and cst_varnish_dict['ip'] != '':
                    consul_varnish_cst['ip'] = cst_varnish_dict['ip']
                    sid_dict['Address'] = consul_varnish_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_varnish_custom/{iid}',consul_varnish_cst)
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

api.add_resource(varnish, '/api/varnish/<stype>')
