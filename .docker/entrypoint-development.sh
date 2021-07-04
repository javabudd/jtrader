#!/bin/bash

make virtualenv

source env/bin/activate

exec "$@"
