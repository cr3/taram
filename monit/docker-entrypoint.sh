#!/bin/bash

env > /opt/monit/scripts/.env

exec "$@"
