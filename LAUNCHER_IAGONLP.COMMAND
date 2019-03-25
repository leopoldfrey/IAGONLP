#!/bin/sh
echo Starting IagoNLP2
export CORENLP_HOME=$(dirname $0)/src/stanford-corenlp-full-2018-10-05
cd $(dirname $0)/src
pwd
python3.7 ./StanfordNLP.py
echo Done