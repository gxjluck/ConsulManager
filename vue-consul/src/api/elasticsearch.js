import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobelasticsearch() {
  return request({
    url: '/api/elasticsearch/jobelasticsearch',
    method: 'get'
  })
}

export function getelasticsearchServicesList() {
  return request({
    url: '/api/elasticsearch/elasticsearch_services',
    method: 'get'
  })
}

export function getelasticsearchConfig(services_dict) {
  return request({
    url: '/api/elasticsearch/elasticsearchpconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getelasticsearchRules() {
  return request({
    url: '/api/elasticsearch/elasticsearchrules',
    method: 'get'
  })
}

export function postCstelasticsearch(cst_elasticsearch_dict) {
  return request({
    url: '/api/elasticsearch/cstelasticsearch',
    method: 'post',
    data: { cst_elasticsearch_dict }
  })
}

export function getCstelasticsearchConfig(iid) {
  return request({
    url: '/api/elasticsearch/cstelasticsearchconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstelasticsearchList(jobelasticsearch_name, checked) {
  return request({
    url: '/api/elasticsearch/cstelasticsearchlist',
    method: 'get',
    params: { jobelasticsearch_name, checked }
  })
}
