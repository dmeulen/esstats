#!/usr/bin/env python2

import time
import socket
import logging
import sys
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from collections import MutableMapping
from re import sub
from argparse import ArgumentParser

def parse():
    """Parse commandline arguments"""
    parser = ArgumentParser()
    parser.add_argument('--es-hosts', '-e', help="Elasticsearch master nodes", default="localhost")
    parser.add_argument('--carbon-server', '-c', help="Carbon server", default="localhost")
    parser.add_argument('--carbon-port', '-p', help="Corbon port", type=int, default="2003")
    parser.add_argument('--state-index', '-s', help="Index to use for keeping a lock", default=".es_stats_lock")
    parser.add_argument('--lock-ttl', '-t', help="Ttl for lock in elasticsearch", default="120s")
    parser.add_argument('--verbose', '-v', help="Be verbose, useful for debugging", action="store_true")

    return parser.parse_args()


def runnable(es, index, lock_ttl):
    """Check if no other master has the lock set"""
    res = ''
    runnable = False
    index_mapping = {
            "mappings" : {
                "lock" : {
                    "_ttl" : {
                        "enabled" : True
                        }
                    }
                }
            }

    doc = { "active_host" : socket.gethostname() }

    if not es.indices.exists(index=index):
        print "Creating index"
        es.indices.create(index=index, body=index_mapping)

    try:
        res = es.get(index=index, doc_type='lock', id=1)
    except NotFoundError:
        es.create(index=index, doc_type='lock', id=1, ttl=lock_ttl, body=doc)
        res = es.get(index=index, doc_type='lock', id=1)
    except:
        print "Unexpected error: sys.exc_info()[0]"
        raise

    if res['_source']['active_host'] == socket.gethostname():
        es.index(index=index, doc_type='lock', id=1, ttl=lock_ttl, body=doc)
        runnable = True

    return runnable


def format4graphite(d, parent_key='', sep='.'):
    """Format graphite datasource name"""
    items = []
    for key, v in d.items():
        k = sub('\.', '_', key)
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(format4graphite(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def main():
    args = parse()
    log = logging.getLogger('elasticsearch-graphite')
    es = Elasticsearch(args.es_hosts.split(','))

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not runnable(es, args.state_index, args.lock_ttl):
        log.debug('Not runnable, bailing out')
        sys.exit(0)
    else:
        sock = socket.socket()
        sock.settimeout(5.0)

        try:
            sock.connect((args.carbon_server, args.carbon_port))
        except:
            log.debug("Could not connect to graphite on {}:{}".format(args.carbon_server, args.carbon_port))
            raise

        node_stats = es.nodes.stats()
        cluster_name = node_stats['cluster_name']
        named_node_stats = {}

        for k, v in node_stats['nodes'].iteritems():
            node_name = node_stats['nodes'][k]['name']
            named_node_stats[node_name] = v

        stats = [
            format4graphite(named_node_stats),
            format4graphite(es.cluster.stats()),
            format4graphite(es.indices.stats())
            ]

        for d in stats:
            for k, v in d.iteritems():
                if isinstance(v, int) and not v < 0:
                    metrics = 'elasticsearch.{}.{} {} {}'.format(cluster_name, k, v, int(time.time()))
                    log.debug(metrics)
                    try:
                        sock.sendall(metrics + '\n')
                    except:
                        log.debug("Could not send metrics...")
                        sys.exit(1)

if __name__ == '__main__':
    main()
