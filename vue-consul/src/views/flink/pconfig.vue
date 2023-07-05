<template>
  <div class="app-container">
    <el-select v-model="services" multiple placeholder="选择需要自动发现的flink组" filterable collapse-tags clearable style="width: 280px" class="filter-item">
      <el-option v-for="item in services_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-input v-model="exporter" placeholder="flink_Exporter IP端口" clearable style="width: 200px;" class="filter-item" />&nbsp;&nbsp;
    <el-select v-model="jobflink" multiple placeholder="选择需要采集指标的flink组" filterable collapse-tags clearable style="width: 340px" class="filter-item">
      <el-option v-for="item in jobflink_list" :key="item" :label="item" :value="item" />
    </el-select>
    <el-input v-model="cm_exporter" placeholder="ConsulManager IP端口" clearable style="width: 190px;" class="filter-item" />&nbsp;&nbsp;
    <el-button class="filter-item" type="primary" icon="el-icon-magic-stick" @click="fetchflinkConfig">
      生成配置
    </el-button>
    <el-button v-clipboard:copy="configs" v-clipboard:success="onCopy" v-clipboard:error="onError" class="filter-item" type="warning" icon="el-icon-document-copy">
      复制配置
    </el-button>
    <pre v-highlightjs="configs" style="line-height:120%"><code class="yaml yamlcode" /></pre>
  </div>
</template>

<script>
import { getflinkServicesList, getflinkConfig, getJobflink } from '@/api/flink'
export default {
  data() {
    return {
      listLoading: false,
      services: [],
      jobflink: [],
      ostype: [],
      services_list: [],
      services_dict: {},
      jobflink_list: [],
      exporter: '',
      cm_exporter: '',
      configs: '该功能用于生成Prometheus的两个JOB配置，生成后请复制到Prometheus配置中：\n\n1. 选择需要同步的账号，Prometheus即可自动发现该账号下的所有flink实例。\n\n2. 由于flink_Exporter无法监控到云flink的CPU、部分云资源使用率的情况，所以ConsulManager开发了Exporter功能，配置到Prometheus即可直接从云厂商采集到这些指标！\n   选择需要采集指标的flink账号区域，即可生成Prometheus的JOB配置。'
    }
  },
  created() {
    this.fetchflinkList()
  },
  methods: {
    onCopy() {
      this.$message({
        message: '复制成功！',
        type: 'success'
      })
    },
    onError() {
      this.$message.error('复制失败！')
    },
    fetchflinkList() {
      this.listLoading = true
      getflinkServicesList().then(response => {
        this.services_list = response.services_list
        this.services_list.push('selfflink_exporter')
      })
      getJobflink().then(response => {
        this.jobflink_list = response.jobflink
      })
      this.listLoading = false
    },
    fetchflinkConfig() {
      this.listLoading = true
      this.services_dict.services_list = this.services
      this.services_dict.exporter = this.exporter
      this.services_dict.jobflink_list = this.jobflink
      this.services_dict.cm_exporter = this.cm_exporter
      getflinkConfig(this.services_dict).then(response => {
        this.configs = response.configs
        this.listLoading = false
      })
    }
  }
}
</script>
<style>
  .yamlcode {
    font-family:'Consolas';
  }
  pre {
    max-height: 640px;
    white-space: pre-wrap;
    overflow:auto;
  }
</style>
