#! /usr/bin/env bash
bug=2796383
if [[ $1 == "--hwut-info" ]]; then
    echo "sphericalcow: $bug 0.39.3 does not handle token_type without distinct section;"
    echo "CHOICES: case-1, case-2;"
    exit
fi

tmp=`pwd`
cd $bug/ 
quex -i $1.qx -o Simple
cat Simple-token-class | awk '/set\_/ { print; } /get\_/ { print; } /union/ { print; } /content/ { print; }'

# cleansening
rm -f Simple*
cd $tmp
