#!/bin/sh
echo Starting IagoNLP
export PYTHONPATH=$(dirname $0)/libs:$(dirname $0)/src/
cd $(dirname $0)/src
python -W ignore ./StanfordNLP.py
echo Done