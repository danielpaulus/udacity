#!/bin/sh
a=0
while [ "$a" -lt 4000 ]
do
	a=`expr $a + 500`
	python run_sumo_random.py -i $a -s cgn -t 1 2 3 4
done
 

