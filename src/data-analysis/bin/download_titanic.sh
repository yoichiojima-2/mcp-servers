#!/bin/bash

mkdir -p ./workspace/samples
curl -o ./workspace/samples/titanic.csv https://calmcode.io/static/data/titanic.csv
echo "downloaded titanic dataset."