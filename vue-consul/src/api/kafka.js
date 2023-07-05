import request from '@/utils/request-ops'

export function getResList(job_id) {
  return request({
    url: '/api/nodes/res',
    method: 'get',
    params: { job_id }
  })
}

export function getJobkafka() {
  return request({
    url: '/api/kafka/jobkafka',
    method: 'get'
  })
}

export function getkafkaServicesList() {
  return request({
    url: '/api/kafka/kafka_services',
    method: 'get'
  })
}

export function getkafkaConfig(services_dict) {
  return request({
    url: '/api/kafka/kafkapconfig',
    method: 'post',
    data: { services_dict }
  })
}
export function getkafkaRules() {
  return request({
    url: '/api/kafka/kafkarules',
    method: 'get'
  })
}

export function postCstkafka(cst_kafka_dict) {
  return request({
    url: '/api/kafka/cstkafka',
    method: 'post',
    data: { cst_kafka_dict }
  })
}

export function getCstkafkaConfig(iid) {
  return request({
    url: '/api/kafka/cstkafkaconf',
    method: 'get',
    params: { iid }
  })
}

export function getCstkafkaList(jobkafka_name, checked) {
  return request({
    url: '/api/kafka/cstkafkalist',
    method: 'get',
    params: { jobkafka_name, checked }
  })
}
