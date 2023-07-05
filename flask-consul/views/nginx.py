from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('nginx',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_nginx_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobnginx_name',type=str)
parser.add_argument('checked',type=str)

class nginx(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobnginx':
            jobnginx = consul_kv.get_keys_list('ConsulManager/jobs')
            jobnginx_list = [i.split('/jobs/')[1] for i in jobnginx if '/nginx/' in i]
            return {'code': 20000,'jobnginx':jobnginx_list}
        elif stype == 'nginx_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/nginx/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'nginxrules':
            return gen_config.get_nginxrules()
        elif stype == 'cstnginxconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_nginx_config = consul_kv.get_value(f'ConsulManager/assets/sync_nginx_custom/{iid}')
            cst_nginx_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_nginx_config and cst_nginx_config['ip'] != '':
                cst_nginx_config['ipswitch'] = True
            if 'port' in cst_nginx_config and cst_nginx_config['port'] != '':
                cst_nginx_config['portswitch'] = True
            return {'code': 20000, 'cst_nginx': cst_nginx_config}
        elif stype == 'cstnginxlist':
            args = parser.parse_args()
            jobnginx_name = args['jobnginx_name']
            checked = args['checked']
            cst_nginx_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_nginx_custom/')
            cst_nginx_keylist = [k.split('/')[-1] for k,v in cst_nginx_dict.items() if v != {}]
            nginx_info = consul_kv.get_res_services(jobnginx_name)
            if checked == 'false':
                return nginx_info
            else:
                cst_nginx_list = [i for i in nginx_info['res_list'] if i['iid'] in cst_nginx_keylist]
                return {'code': 20000, 'res_list': cst_nginx_list}
                
    def post(self, stype):
        if stype == 'nginxpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.nginx_config(services_dict['jobnginx_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstnginx':
            args = parser.parse_args()
            cst_nginx_dict = args['cst_nginx_dict']
            consul_nginx_cst = {}
            iid = cst_nginx_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_nginx_dict['portswitch'] and cst_nginx_dict['port'] != '':
                    consul_nginx_cst['port'] = int(cst_nginx_dict['port'])
                    sid_dict['Port'] = consul_nginx_cst['port']
                if cst_nginx_dict['ipswitch'] and cst_nginx_dict['ip'] != '':
                    consul_nginx_cst['ip'] = cst_nginx_dict['ip']
                    sid_dict['Address'] = consul_nginx_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_nginx_custom/{iid}',consul_nginx_cst)
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

api.add_resource(nginx, '/api/nginx/<stype>')
