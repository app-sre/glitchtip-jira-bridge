#!/bin/bash

# create table
awslocal dynamodb create-table --table-name gjb --attribute-definitions AttributeName=key,AttributeType=S --key-schema AttributeName=key,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --table-class STANDARD
awslocal dynamodb create-table --table-name limits --attribute-definitions AttributeName=key,AttributeType=S --key-schema AttributeName=key,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --table-class STANDARD

# set TTL; currently not supported by localstack
awslocal dynamodb update-time-to-live --table-name gjb --time-to-live-specification 'Enabled=true, AttributeName=ttl'
awslocal dynamodb update-time-to-live --table-name limits --time-to-live-specification 'Enabled=true, AttributeName=ttl'
