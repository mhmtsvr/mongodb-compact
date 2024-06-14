import os, time
import logging
import urllib
from db import compact_mongodb, single_host_compact_mongodb

def main():

    print(f"[ {time.strftime('%x %X %Z')} ] - Setting variables...\n")
    host = os.environ.get('DB_ENDPOINT', "localhost")

    # Only host gets updated if a single host will get compacted
    if os.getenv('DB_SINGLE_HOST'):
        host = os.environ['DB_SINGLE_HOST']

    replicaset = os.environ.get('DB_REPLICASET', "replicaset")
    username = os.environ.get('DB_USERNAME', "admin")
    password = urllib.parse.quote_plus(os.environ.get('DB_PASSWORD', "password"))
    mongo_auth_mechanism = os.environ.get('DB_AUTH_MECHANISM', "SCRAM-SHA-256")
    mongo_uri = f'mongodb://{username}:{password}@{host}/admin?replicaSet={replicaset}&authSource=admin&authMechanism={mongo_auth_mechanism}'
    try:
        if os.getenv('DB_SINGLE_HOST'):
            single_host_compact_mongodb(host, replicaset, username, password, mongo_auth_mechanism, mongo_uri)
        else:
            compact_mongodb(host, replicaset, username, password, mongo_auth_mechanism, mongo_uri)
    except Exception as err:
        print('-------------------------------------------------------------------------')
        logging.exception(err)
        print('-------------------------------------------------------------------------')

if __name__ == "__main__":
    main()    