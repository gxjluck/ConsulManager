import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobvarnish() {
  return request({
    url: '/api/varnish/jobvarnish',
    method: 'get'
  })
}

export function getvarnishServicesList() {
  return request({
    url: '/api/varnish/varnish_services',
    method: 'get'
  })
}

export function getvarnishConfig(services_dict) {
  return request({
    url: '/api/varnish/varnishpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getvarnishRules() {
  return request({
    url: '/api/varnish/varnishrules',
    method: 'get'
  })
}

export function postCstvarnish(cst_varnish_dict) {
  return request({
    url: '/api/varnish/cstvarnish',
    method: 'post',
    data: { cst_varnish_dict }
  })
}

export function getCstvarnishConfig(iid) {
  return request({
    url: '/api/varnish/cstvarnishconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstvarnishList(jobvarnish_name, checked) {
  return request({
    url: '/api/varnish/cstvarnishlist',
    method: 'get',
    params: { jobvarnish_name, checked }
  })
}
