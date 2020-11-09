# URL Lookup Web Service

#### Why?
This is a coding test/challenge to show case python use in creating a web service to provide a simple url lookup service.

Examples of such service: 

    https://talosintelligence.com/    
    https://www.brightcloud.com/tools/url-ip-lookup.php

#### Description

We have an HTTP proxy that is scanning traffic looking for malware URLs. Before
allowing HTTP connections to be made, this proxy asks a service that maintains several
databases of malware URLs if the resource being requested is known to contain
malware.

Write a small web service, in the language/framework your choice, that responds to
GET requests where the caller passes in a URL and the service responds with some
information about that URL. The GET requests look like this:

    GET /urlinfo/1/{hostname_and_port}/{original_path_and_query_string}
    
The caller wants to know if it is safe to access that URL or not. As the implementer you
get to choose the response format and structure. These lookups are blocking users
from accessing the URL until the caller receives a response from your service.

The service must be containerized.

Give some thought to the following: (Final Challenges)

1) The size of the URL list could grow infinitely, how might you scale this beyond the memory capacity of this VM? (Bonus if you implement this)
2) The number of requests may exceed the capacity of this VM, how might you solve that? (Bonus if you implement this)
3) What are some strategies you might use to update the service with new URLs? Updates may be as much as 5 thousand URLs a day with updates arriving every
10 minutes.

#### Hints
* It would be good to "release" frequent updates by pushing updates to a shared git repo
* Don't forget some unit tests (at least something representative).

## Implementation Notes
#### Info:
* SampleMalwareList.txt contains 1104 urls and has been downloaded from: http://www.malwaredomainlist.com/hostslist/hosts.txt
* Implementation uses MariaDB

#### How to use



##### Docker execution:
* Makes sure you have "docker" and "docker-compose" installed properly. 

Step 1:

    Option A) Pulls the pre-build image from docker hub and runs it:

        docker-compose -f docker-compose_noBuild.yaml up
    
    Option B) Builds the web service from source: 
        
         docker-compose up
Note: In both options, prebuilt MariaDB image is pulled.

Step 2:
Find the IP address of the running containers by running:
    
     docker ps
     docker inspect DOCKER_ID | grep IPAddress

Note: To build the image for the urllookup web service, run something like:

      docker build -t urllookup .
     or 
      docker build -t youebr/urllookup:11072020 .

##### Manual execution:
* Environment Setup: Ubuntu 20.04.1 LTS, 10.3.25-MariaDB-0ubuntu0.20.04.1, Python 3.8.5
* Package installs:

        sudo apt install -y mariadb-server libmariadb-dev python3-pip
        pip3 install -r requirements.txt  (pip3 install flask, pip3 install mariadb, pip3 install waitress)

* To run the web server

        python3 run.py

* To run the unittests

        python3 -m unittest discover tests


#### Final Challenges
See Description section for detail of each challenge.

1- TODO

2- To address this issue, an NginX loadbalancer is added to direct the incoming traffic to any of the running instances of urllookup web app.
To implement this,  nginx/nginx.conf, nginx/Dockerfile, and docker-compose_loadbalancer.yaml are added. To run the web service with loadbalancer, do:

         docker-compose -f docker-compose_loadbalancer.yaml up --scale urllookup=3 --build
Above command runs 3 instances of urlookup web app and load balances among them in round robin mode. To see it in action, run the above command, then direct your browser to  http://localhost:8080/urlinfo/1/google.com and refresh the page multiple times.  On terminal, you should see logs marked with the name of instances, e.g urllookup_1, urllookup_2, urllookup_3   

###### Good to have: 
* Right now, DB initialization is done in Python code (web service). It can be moved to MariaDB container (entrypoint-initdb) simialr to the implementation done in  https://github.com/YouEbr/mariadb_docker_init

3- TODO

#### Miscellaneous
 To allow running MariaDB without "sudo", in order words, if you are receiving following error:
 
        Access denied for user 'root'@'localhost'
 
After installing mariadb, first run it with sudo like:

        mariadb -u root
Then   
   
        SELECT User,Host FROM mysql.user;    
        DROP USER 'root'@'localhost';
        CREATE USER 'root'@'%' IDENTIFIED BY '';
        GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
        SELECT User,Host FROM mysql.user;
        CREATE USER 'YOUR USER NAME'@'%' IDENTIFIED BY ''; [optional: to use your username instead of root] 
        SELECT User,Host FROM mysql.user;  
