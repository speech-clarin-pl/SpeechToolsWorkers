# Speech Tools Workers

RabbitMQ workers for the Clarin-PL speech tools website.


## Instructions

* RabbitMQ:

`docker run -d -p 5672:5672 --name rabbitmq rabbitmq:3-management`

* Get management console:

`docker inspect rabbitmq` -> to get the IP

`http://<docker-ip>:15672` -> to get the console (login guest/guest)

* Running daemon:

`docker run --link rabbitmq:rabbitmq danijel3/clarin-pl-daemon -v /path/to/work:/work`