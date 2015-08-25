# esstats
Elasticsearch stats for graphite, this is a WIP. Works but needs a bit of work.
Should run as a cron job on the master nodes.

```
usage: es_stats.py [-h] [--es-hosts ES_HOSTS] [--carbon-server CARBON_SERVER]
                   [--carbon-port CARBON_PORT] [--state-index STATE_INDEX]
                   [--lock-ttl LOCK_TTL] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --es-hosts ES_HOSTS, -e ES_HOSTS
                        Elasticsearch master nodes
  --carbon-server CARBON_SERVER, -c CARBON_SERVER
                        Carbon server
  --carbon-port CARBON_PORT, -p CARBON_PORT
                        Corbon port
  --state-index STATE_INDEX, -s STATE_INDEX
                        Index to use for keeping a lock
  --lock-ttl LOCK_TTL, -t LOCK_TTL
                        Ttl for lock in elasticsearch
  --verbose, -v         Be verbose, useful for debugging
```
