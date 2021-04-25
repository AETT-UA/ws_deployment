#!/bin/bash

#echo "USAGE: $0 [ports...] "
#echo "Some examples:"
#    echo "  $0 8000 8001          (kills processes on ports 8000 and 8001)"

for arg; do
	echo "Killing process on port $arg..."
	processes=( $(lsof -t -i:$arg ) )
	for p in "${processes[@]}"
	do
		eval "kill -9 $p 2> /dev/null"
	done


done
