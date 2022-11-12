#!/bin/bash

set -e

for file in ./*.py
do
  
  echo "=================run test $file========================"
  pytest $file
  echo "=================run test $file complete!=============="

done