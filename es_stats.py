#!/usr/bin/env python2

import time
import socket
import logging
from elasticsearch import Elasticsearch
from collections import MutableMapping
from re import sub
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('--es-hosts', '-e', help="Elasticsearch master nodes", default="localhost")
parser.add_argument('--carbon-server', '-c', help="Carbon server", default="localhost")
parser.add_argument('--carbon-port', '-p', help="Corbon port", type=int, default="2003")
parser.add_argument('--interval', '-i', help="Check interval in seconds", type=int, default=10)
parser.add_argument('--state-index', '-s', help="Index to use for keeping state", default="state_index")
parser.add_argument('--verbose', '-v', help="Be verbose, useful for debugging", action="store_true")

log = logging.getLogger('elasticsearch-graphite')

def flatten(d, parent_key='', sep='.'):
    """Flatten dicts when nested"""
    items = []
    for key, v in d.items():
        k = sub('\.', '_', key)
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)

def main():
    args = parser.parse_args()
    es = Elasticsearch(args.es_hosts.split(','))

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    while True:
        sock = socket.socket()
        sock.settimeout(5.0)

        try:
            sock.connect((args.carbon_server, args.carbon_port))
        except:
            log.debug("Could not connect to graphite on {}:{}".format(args.carbon_server, args.carbon_port))
            time.sleep(2)
            continue

        while True:
            node_stats = es.nodes.stats()
            cluster_name = node_stats['cluster_name']
            named_node_stats = {}

            for k, v in node_stats['nodes'].iteritems():
                node_name = node_stats['nodes'][k]['name']
                named_node_stats[node_name] = v

            stats = [
                flatten(named_node_stats),
                flatten(es.cluster.stats()),
                flatten(es.indices.stats())
                ]

            for d in stats:
                for k, v in d.iteritems():
                    if isinstance(v, int):
                        metrics = 'elasticsearch.{}.{} {} {}'.format(cluster_name, k, v, int(time.time()))
                        log.debug(metrics)
                        try:
                            sock.sendall(metrics + '\n')
                        except:
                            log.debug("Could not send metrics...")
                            break

            else:
                time.sleep(args.interval)
                continue
            break

if __name__ == '__main__':
    main()
