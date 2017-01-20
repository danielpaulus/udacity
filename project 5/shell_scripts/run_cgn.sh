#!/bin/sh
a=0
while [ True ]
do
	a=`expr $a + 500`
	python dqn_main.py -i $a -s cgn --fulldqn -c 0 -t 1 2 3 4
done

