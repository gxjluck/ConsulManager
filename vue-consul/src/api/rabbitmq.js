import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobrabbitmq() {
  return request({
    url: '/api/rabbitmq/jobrabbitmq',
    method: 'get'
  })
}

export function getrabbitmqServicesList() {
  return request({
    url: '/api/rabbitmq/rabbitmq_services',
    method: 'get'
  })
}

export function getrabbitmqConfig(services_dict) {
  return request({
    url: '/api/rabbitmq/rabbitmqpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getrabbitmqRules() {
  return request({
    url: '/api/rabbitmq/rabbitmqrules',
    method: 'get'
  })
}

export function postCstrabbitmq(cst_rabbitmq_dict) {
  return request({
    url: '/api/rabbitmq/cstrabbitmq',
    method: 'post',
    data: { cst_rabbitmq_dict }
  })
}

export function getCstrabbitmqConfig(iid) {
  return request({
    url: '/api/rabbitmq/cstrabbitmqconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstrabbitmqList(jobrabbitmq_name, checked) {
  return request({
    url: '/api/rabbitmq/cstrabbitmqlist',
    method: 'get',
    params: { jobrabbitmq_name, checked }
  })
}
