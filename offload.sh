#!/bin/bash

echo
echo 
echo

runTest="$1 -app $2 testsuite --no-colors app $3 > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt"

# $1 -app $2 testsuite --no-colors app $3 > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt
# $1 -app $2 testsuite --no-colors app $3 > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt
# $runTest > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt
# echo $runTest > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt
eval $runTest > /Volumes/Mondrian/Users/joaquin/Sites/fictionesque2.0/app/cosa.txt