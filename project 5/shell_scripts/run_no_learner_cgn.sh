#!/bin/sh
a=0
while [ True ]
do
	a=`expr $a + 500`
	python run_sumo_nolearner.py -i $a -s cgn
done
 

