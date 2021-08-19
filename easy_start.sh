#!/bin/bash

git pull https://github.com/savelbl4/simple_infra

pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests pykeepass
 # > /dev/null

python3 main.py