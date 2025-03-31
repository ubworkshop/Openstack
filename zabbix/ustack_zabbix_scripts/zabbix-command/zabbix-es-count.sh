#!/usr/bin/bash
curl -XGET -s  "http://localhost:9200/openstack-*/fluentd/_count?pretty" -d'
{
  "post_filter": {
    "range": {
      "@timestamp": {
        "from": "now-5m",
        "to": "now"
      }
    }
  }
}'|jq '.count'
