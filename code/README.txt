    ____                   __           __
   / __ \  ____   _____   / /__  ___   / /_
  / /_/ / / __ \ / ___/  / //_/ / _ \ / __/
 / _, _/ / /_/ // /__   / ,<   /  __// /_
/_/ |_|  \____/ \___/  /_/|_|  \___/ \__/

# Running Requirements #

- Software
-- Python 3 with following libs:
    flask
    alpha_vantage
    arrow
    numpy
    sklearn
    tensorflow
    pymongo
-- MongoDB 4.0 or above
-- "env.py" with API key
-- port 27017, 8081, 80, 5001 available

- Hardware
--1GiB storage space or above
--4GiB RAM and swap space or above
--Internet access


# Project Dev Env #

- OS :
-- MacOS Mojave 0.14.4(18E226)
-- Python 3.6.1
-- MongoDB 4.0


# Application Launching Instructions #

- Install Dependencies
-- Install Python 3 with all libs quoted above
-- Install MongoDB 4.0+
    check: 'https://docs.mongodb.com/manual/installation/'
-- Install a web browser on your system

- Activate MongoDB
-- Start MongoDB service
-- Import database files from json
    all three databases are under './stockapp'
    to import them, check: 'https://docs.mongodb.com/manual/reference/program/mongoimport/'

- Deploy API key
-- Store a "env.py" file under './rocket/engine/'
-- modify the env file as follows:
    '''

    class Env:
        alpha_vantage_api_key = "YOUR_API_KEY"

    '''

- Launch The Rocket
-- In a terminal with project path specified, type:
    '''

    python ./rocket/launch.py

    '''
-- Open browser and visit 'http://0.0.0.0:5001/'