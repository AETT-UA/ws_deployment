#!/bin/bash
usage(){
	echo "USAGE: $0 [--rest-port <port> --database <database>] [--interface <interface to use> --interface-port <port>]"
    echo "  --rest-port <port>                      port where the rest api will be available"
    echo "  --interface-port <port>                 port where the interface will be available"
    echo ""
    echo "Some examples:"
    echo "  $0 --rest-port 9000 --interface-port 8000"

    
	exit 1
}


while test -n "$1"; do
    case "$1" in
      -h|--help)
          usage ;
          shift 2
          ;; 

      -rp|--rest-port)
          rest_port=$2
          shift 2
          ;; 
 
      -ip|--interface-port)
          interface_port=$2
          shift 2
          ;;
	*)
	  shift 2
	  ;;  
    esac
done  


# if we have both the database and the port
if [ ! -z "$rest_port" ]; then
    echo "Running the REST API on port $rest_port."
    eval "cd rest_api &&  pip3 install -r requirements.txt && rm -rf api/migrations && nohup python3 manage.py makemigrations api && python3 manage.py migrate && python3 manage.py runserver $rest_port &"
else
    exit 1
fi

# if we have both the interface and the port
if  [ ! -z "$interface_port" ]; then
    echo "Running the simple html+js+css interface on the port $interface_port."
    eval "cd interface && pip3 install -r requirements.txt && nohup python3 -m http.server &"
else
    exit 1
fi


