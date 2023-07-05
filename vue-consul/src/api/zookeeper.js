import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobzookeeper() {
  return request({
    url: '/api/zookeeper/jobzookeeper',
    method: 'get'
  })
}

export function getzookeeperServicesList() {
  return request({
    url: '/api/zookeeper/zookeeper_services',
    method: 'get'
  })
}

export function getzookeeperConfig(services_dict) {
  return request({
    url: '/api/zookeeper/zookeeperpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getzookeeperRules() {
  return request({
    url: '/api/zookeeper/zookeeperrules',
    method: 'get'
  })
}

export function postCstzookeeper(cst_zookeeper_dict) {
  return request({
    url: '/api/zookeeper/cstzookeeper',
    method: 'post',
    data: { cst_zookeeper_dict }
  })
}

export function getCstzookeeperConfig(iid) {
  return request({
    url: '/api/zookeeper/cstzookeeperconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstzookeeperList(jobzookeeper_name, checked) {
  return request({
    url: '/api/zookeeper/cstzookeeperlist',
    method: 'get',
    params: { jobzookeeper_name, checked }
  })
}
