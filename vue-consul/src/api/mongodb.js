import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobmongodb() {
  return request({
    url: '/api/mongodb/jobmongodb',
    method: 'get'
  })
}

export function getmongodbServicesList() {
  return request({
    url: '/api/mongodb/mongodb_services',
    method: 'get'
  })
}

export function getmongodbConfig(services_dict) {
  return request({
    url: '/api/mongodb/mongodbpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getmongodbRules() {
  return request({
    url: '/api/mongodb/mongodbrules',
    method: 'get'
  })
}

export function postCstmongodb(cst_mongodb_dict) {
  return request({
    url: '/api/mongodb/cstmongodb',
    method: 'post',
    data: { cst_mongodb_dict }
  })
}

export function getCstmongodbConfig(iid) {
  return request({
    url: '/api/mongodb/cstmongodbconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstmongodbList(jobmongodb_name, checked) {
  return request({
    url: '/api/mongodb/cstmongodblist',
    method: 'get',
    params: { jobmongodb_name, checked }
  })
}
