import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobflink() {
  return request({
    url: '/api/flink/jobflink',
    method: 'get'
  })
}

export function getflinkServicesList() {
  return request({
    url: '/api/flink/flink_services',
    method: 'get'
  })
}

export function getflinkConfig(services_dict) {
  return request({
    url: '/api/flink/flinkpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getflinkRules() {
  return request({
    url: '/api/flink/flinkrules',
    method: 'get'
  })
}

export function postCstflink(cst_flink_dict) {
  return request({
    url: '/api/flink/cstflink',
    method: 'post',
    data: { cst_flink_dict }
  })
}

export function getCstflinkConfig(iid) {
  return request({
    url: '/api/flink/cstflinkconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstflinkList(jobflink_name, checked) {
  return request({
    url: '/api/flink/cstflinklist',
    method: 'get',
    params: { jobflink_name, checked }
  })
}
