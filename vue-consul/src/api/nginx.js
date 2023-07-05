import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobnginx() {
  return request({
    url: '/api/nginx/jobnginx',
    method: 'get'
  })
}

export function getnginxServicesList() {
  return request({
    url: '/api/nginx/nginx_services',
    method: 'get'
  })
}

export function getnginxConfig(services_dict) {
  return request({
    url: '/api/nginx/nginxpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getnginxRules() {
  return request({
    url: '/api/nginx/nginxrules',
    method: 'get'
  })
}

export function postCstnginx(cst_nginx_dict) {
  return request({
    url: '/api/nginx/cstnginx',
    method: 'post',
    data: { cst_nginx_dict }
  })
}

export function getCstnginxConfig(iid) {
  return request({
    url: '/api/nginx/cstnginxconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstnginxList(jobnginx_name, checked) {
  return request({
    url: '/api/nginx/cstnginxlist',
    method: 'get',
    params: { jobnginx_name, checked }
  })
}
