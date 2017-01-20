#!/bin/sh
a=0
while [ "$a" -lt 8500 ]
do
	a=`expr $a + 500`
	python run_sumo_random.py -i $a -s lust -t 4 6 7
done
 

