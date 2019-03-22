#!/bin/sh
echo Starting NLP
cd $(dirname $0)/src/stanford-corenlp-full-2018-10-05
sh ./corenlp.sh -port 9000 -timeout 15000 -annotator tokenize ssplit pos lemma ner -lang fr
echo Done