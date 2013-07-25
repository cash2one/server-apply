#!/bin/bash

ROOT=$(cd "$(dirname "$0")"; pwd)

scp -r $ROOT/run.py $ROOT/config.py $ROOT/sa/ root@apc10-001.i.ajkdns.com:/opt/server-apply
