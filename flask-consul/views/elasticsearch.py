from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from flask_apscheduler import APScheduler
import traceback
#import sys
#sys.path.append("..")
from units import token_auth,consul_kv,gen_config,consul_svc
from units.config_log import *
blueprint = Blueprint('elasticsearch',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('job_id',type=str)
parser.add_argument('services_dict',type=dict)
parser.add_argument('cst_elasticsearch_dict',type=dict)
parser.add_argument('iid',type=str)
parser.add_argument('jobelasticsearch_name',type=str)
parser.add_argument('checked',type=str)

class elasticsearch(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self, stype):
        job_id = parser.parse_args()['job_id']
        if stype == 'jobelasticsearch':
            jobelasticsearch = consul_kv.get_keys_list('ConsulManager/jobs')
            jobelasticsearch_list = [i.split('/jobs/')[1] for i in jobelasticsearch if '/elasticsearch/' in i]
            return {'code': 20000,'jobelasticsearch':jobelasticsearch_list}
        elif stype == 'elasticsearch_services':
            jobecs = consul_kv.get_keys_list('ConsulManager/jobs')
            jobecs_list = [i.split('/jobs/')[1] for i in jobecs if '/elasticsearch/' in i]
            services_list = []
            for i in jobecs_list:
                serivces = i.split("/")
                services_list.append(f'{serivces[0]}_{serivces[1]}_{serivces[2]}')
            return {'code': 20000,'services_list': sorted(set(services_list))}
        elif stype == 'elasticsearchrules':
            return gen_config.get_elasticsearchrules()
        elif stype == 'cstelasticsearchconf':
            args = parser.parse_args()
            iid = args['iid']
            cst_elasticsearch_config = consul_kv.get_value(f'ConsulManager/assets/sync_elasticsearch_custom/{iid}')
            cst_elasticsearch_config.update({'iid': iid,'ipswitch': False,'portswitch': False})
            if 'ip' in cst_elasticsearch_config and cst_elasticsearch_config['ip'] != '':
                cst_elasticsearch_config['ipswitch'] = True
            if 'port' in cst_elasticsearch_config and cst_elasticsearch_config['port'] != '':
                cst_elasticsearch_config['portswitch'] = True
            return {'code': 20000, 'cst_elasticsearch': cst_elasticsearch_config}
        elif stype == 'cstelasticsearchlist':
            args = parser.parse_args()
            jobelasticsearch_name = args['jobelasticsearch_name']
            checked = args['checked']
            cst_elasticsearch_dict = consul_kv.get_kv_dict('ConsulManager/assets/sync_elasticsearch_custom/')
            cst_elasticsearch_keylist = [k.split('/')[-1] for k,v in cst_elasticsearch_dict.items() if v != {}]
            elasticsearch_info = consul_kv.get_res_services(jobelasticsearch_name)
            if checked == 'false':
                return elasticsearch_info
            else:
                cst_elasticsearch_list = [i for i in elasticsearch_info['res_list'] if i['iid'] in cst_elasticsearch_keylist]
                return {'code': 20000, 'res_list': cst_elasticsearch_list}
                
    def post(self, stype):
        if stype == 'elasticsearchpconfig':
            args = parser.parse_args()
            services_dict = args['services_dict']
            return gen_config.elasticsearch_config(services_dict['jobelasticsearch_list'],services_dict['cm_exporter'],services_dict['services_list'],services_dict['exporter'])
        elif stype == 'cstelasticsearch':
            args = parser.parse_args()
            cst_elasticsearch_dict = args['cst_elasticsearch_dict']
            consul_elasticsearch_cst = {}
            iid = cst_elasticsearch_dict['iid']
            try:
                sid_dict = consul_svc.get_sid(iid)['instance']
                if cst_elasticsearch_dict['portswitch'] and cst_elasticsearch_dict['port'] != '':
                    consul_elasticsearch_cst['port'] = int(cst_elasticsearch_dict['port'])
                    sid_dict['Port'] = consul_elasticsearch_cst['port']
                if cst_elasticsearch_dict['ipswitch'] and cst_elasticsearch_dict['ip'] != '':
                    consul_elasticsearch_cst['ip'] = cst_elasticsearch_dict['ip']
                    sid_dict['Address'] = consul_elasticsearch_cst['ip']
                consul_kv.put_kv(f'ConsulManager/assets/sync_elasticsearch_custom/{iid}',consul_elasticsearch_cst)
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

api.add_resource(elasticsearch, '/api/elasticsearch/<stype>')
