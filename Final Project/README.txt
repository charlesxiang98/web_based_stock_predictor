README

---- running requirements ----
an OS that can run docker-ce and docker-compose on it
2GiB+ free space in storage
enough RAM and swap space
Internet access
port 27017, 8081, 80, 5001 are available

---- the project is developed under ----
- OS :
  Linux ip-172-31-31-149 4.4.0-1052-aws #61-Ubuntu SMP Mon Feb 12 23:05:58 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
- docker :
  Server Version: 17.12.1-ce
  Storage Driver: overlay2
- docker-compose :
  docker-compose version 1.19.0, build 9e633ef
  docker-py version: 2.7.0
  CPython version: 2.7.13
  OpenSSL version: OpenSSL 1.0.1t  3 May 2016

---- HOW TO install and run the application ----
1. install docker-ce and docker-compose follow the instruction (the web address may changed):
  - docker-ce : https://docs.docker.com/install/
  - docker-compose : https://docs.docker.com/compose/install/
  [if you already installed docker-ce and docker-compose please make sure they are in the latest version]

2. download, unzip and copy the whole folder to you work dir.

3. set up secret files:
for safety reasons, some sensitive information dose not appear directly in the project
these information are loaded to the project from local files
so please set up those files in your  work dir (the root dir of the project (the folder where file docker-compose.yml is in))
and save the relative information in those files: [you may use (echo "something" >> file_name) or something similar]
  - alphavantag_api_key
    the alphavantag API key.
  - mongo_initdb_root_password
    the admin password of MongoDB

4. set up the config file of mongo-express
- line 70 : adminUsername: process.env.ME_CONFIG_MONGODB_ADMINUSERNAME || '',
  put you mongodb admin username which is the value of environment MONGO_INITDB_ROOT_USERNAME between apostrophes
  e.g. adminUsername: process.env.ME_CONFIG_MONGODB_ADMINUSERNAME || 'your mongodb admin username',
- line 71 : adminPassword: process.env.ME_CONFIG_MONGODB_ADMINPASSWORD || '',
  put you mongodb admin password which is in the file mongo_initdb_root_password between apostrophes
  e.g. adminUsername: process.env.ME_CONFIG_MONGODB_ADMINPASSWORD || 'your mongodb admin password',
- line 100 : username: process.env.ME_CONFIG_BASICAUTH_USERNAME || 'admin',
  change the admin between apostrophes to what you wnt for the username of mongo-express web page
  e.g. username: process.env.ME_CONFIG_BASICAUTH_USERNAME || 'root',
- line 101 : password: process.env.ME_CONFIG_BASICAUTH_PASSWORD || 'pass',
  change the pass between apostrophes to what you wnt for the password of mongo-express web page
  e.g. password: process.env.ME_CONFIG_BASICAUTH_PASSWORD || 'toor',

5. set up environment variables in docker-compose.yml
there are some environment variables which are already set up you can change it if you want
the environment variables are in docker-compose.yml under environment in each services
- ALPHAVANTAG_API_KEY_FILE
  please DO NOT modify
- MONGO_INITDB_ROOT_USERNAME
  the root username of mongodb
- MONGO_INITDB_ROOT_PASSWORD_FILE
  please DO NOT modify
- MONGO_HOST
  please DO NOT modify
- PYTHONUNBUFFERED
  please DO NOT modify
- ME_CONFIG_MONGODB_SERVER
  please DO NOT modify

6. modify the stocks which you want retrieve
in file docker-compose.yml in services: get-stock-data: command
from the 3rd element to the end are the stock names input to the application as args
you can modify them

7. run the application and CONGRATULATIONS \^o^/
run the command to start the application under the root dir of project with enough privilege
[you may use sudo under linux and something similar in Windows and macOS]
foreground : docker-compose up --build
Detached mode : docker-compose up --build -d

8. access to the database
open yourcomputer:8081 in browser
the address may localhost:8081 yourIP:8081 yourcomputername:8081 domainname:8081 etc.
it depends on your network and your ISP and how you running the application (local or in remote server)

9. to stop the detached mode application
docker-compose down
