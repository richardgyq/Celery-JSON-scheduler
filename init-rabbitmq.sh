#!/bin/sh

# Create Default RabbitMQ setup
( sleep 5 ; \

# enable management plugin
rabbitmq-plugins enable rabbitmq_management
 
# Create users
rabbitmqctl add_user rabbitmquser rabbitmquser
rabbitmqctl add_user rabbitmqadmin rabbitmqadmin

# Set user rights
rabbitmqctl set_user_tags rabbitmquser rabbitmquser
rabbitmqctl set_user_tags rabbitmqadmin administrator

# Create vhosts
rabbitmqctl add_vhost rabbitmqvhost

# Set vhost permissions
rabbitmqctl set_permissions -p rabbitmqvhost rabbitmquser ".*" ".*" ".*"
rabbitmqctl set_permissions -p / rabbitmqadmin ".*" ".*" ".*"
rabbitmqctl set_permissions -p rabbitmqvhost rabbitmqadmin ".*" ".*" ".*"

# # enable mqtt plugin
# rabbitmq-plugins enable rabbitmq_mqtt
) &    
rabbitmq-server $@
