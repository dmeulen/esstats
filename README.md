# esstats
Elasticsearch stats for graphite, this is a WIP. Works but needs a bit of work.
Should run under supervision of supervisor or upstart.

  usage: es_stats.py [-h] [--es-hosts ES_HOSTS] [--carbon-server CARBON_SERVER]
                     [--carbon-port CARBON_PORT] [--interval INTERVAL]
                     [--state-index STATE_INDEX] [--verbose]

  optional arguments:
    -h, --help            show this help message and exit
    --es-hosts ES_HOSTS, -e ES_HOSTS
                          Elasticsearch master nodes
    --carbon-server CARBON_SERVER, -c CARBON_SERVER
                          Carbon server
    --carbon-port CARBON_PORT, -p CARBON_PORT
                          Corbon port
    --interval INTERVAL, -i INTERVAL
                          Check interval in seconds
    --state-index STATE_INDEX, -s STATE_INDEX
                          Index to use for keeping state
    --verbose, -v         Be verbose, useful for debugging

