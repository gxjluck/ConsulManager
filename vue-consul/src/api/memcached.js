import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobmemcached() {
  return request({
    url: '/api/memcached/jobmemcached',
    method: 'get'
  })
}

export function getmemcachedServicesList() {
  return request({
    url: '/api/memcached/memcached_services',
    method: 'get'
  })
}

export function getmemcachedConfig(services_dict) {
  return request({
    url: '/api/memcached/memcachedpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getmemcachedRules() {
  return request({
    url: '/api/memcached/memcachedrules',
    method: 'get'
  })
}

export function postCstmemcached(cst_memcached_dict) {
  return request({
    url: '/api/memcached/cstmemcached',
    method: 'post',
    data: { cst_memcached_dict }
  })
}

export function getCstmemcachedConfig(iid) {
  return request({
    url: '/api/memcached/cstmemcachedconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstmemcachedList(jobmemcached_name, checked) {
  return request({
    url: '/api/memcached/cstmemcachedlist',
    method: 'get',
    params: { jobmemcached_name, checked }
  })
}
