import os, time
import logging
from pymongo.errors import OperationFailure, AutoReconnect
from pymongo import MongoClient

def compact_mongodb(host, replicaset, username, password, mongo_auth_mechanism, mongo_uri):

    try:

        # Connection to the replicaset
        client = MongoClient(mongo_uri)

        # Get the current primary node
        primary = client.get_database("admin").command("ismaster")["primary"].split(":")[0]

        # Get all the secondary nodes
        secondaries = [host[0] for host in client.nodes if host[0] != primary]

        
        # Print storage size values of each DB before compacting
        print("Storage size of each databases before compacting:\n")
        check_storage_size(client)

        for secondary in secondaries:
            # Make sure each node is healthy before proceeding to each node
            check_mongodb_health(client)
            secondary_client = MongoClient(f"mongodb://{username}:{password}@{secondary}:27017/?directConnection=true&authMechanism={mongo_auth_mechanism}")
            print(f"[ {time.strftime('%x %X %Z')} ] - Compacting secondary node ({secondary})")
            for db in secondary_client.list_databases():
                if db["name"] not in ["admin", "local", "config"]:
                    print(f"[ {time.strftime('%x %X %Z')} ] - ** Database {db['name']} being compacted now **")
                    db = secondary_client[db["name"]]
                    for collection in db.list_collection_names():
                        try:
                            result = db.command({"compact": collection})
                            print(f"[ {time.strftime('%x %X %Z')} ] - {collection}@{secondary} : {result}")
                        except OperationFailure as e:
                            print(f"[ {time.strftime('%x %X %Z')} ] - Skipping compact for {collection} on {secondary}: {e}")
            print(f"-------------------------------------------------------------------------\n")
        
        print(f"[ {time.strftime('%x %X %Z')} ] - Waiting 30 secs...")
        time.sleep(30)
        
        print(f"[ {time.strftime('%x %X %Z')} ] - Checking the nodes health status...")
        check_mongodb_health(client)

        # Switch primary
        try:
            print(f"[ {time.strftime('%x %X %Z')} ] - Stepping down the primary node")
            client.get_database("admin").command("replSetStepDown", 60)
        except AutoReconnect:
            pass

        print(f"[ {time.strftime('%x %X %Z')} ] - Waiting 30 secs...")
        time.sleep(30)
        
        print(f"[ {time.strftime('%x %X %Z')} ] - Checking the nodes health status...")
        check_mongodb_health(client)

        # Connect to the old primary node and run the compact command for all databases except admin, local, and config
        old_primary_client = MongoClient(f"mongodb://{username}:{password}@{primary}:27017/?directConnection=true&authMechanism={mongo_auth_mechanism}")
        print(f"[ {time.strftime('%x %X %Z')} ] - Compacting the previous primary node ({primary})")
        for db in old_primary_client.list_databases():
            if db["name"] not in ["admin", "local", "config"]:
                db = old_primary_client[db["name"]]
                for collection in db.list_collection_names():
                    try:
                        result = db.command({"compact": collection})
                        print(f"[ {time.strftime('%x %X %Z')} ] - {collection}@{primary}: {result}")
                    except OperationFailure as e:
                        print(f"[ {time.strftime('%x %X %Z')} ] - Skipping compact for {collection} on {primary}: {e}")
        print(f"-------------------------------------------------------------------------\n")

        print(f"[ {time.strftime('%x %X %Z')} ] - Checking the nodes health status...")
        check_mongodb_health(client)

        # Print storage size values of each DB after compacting
        print("Storage size of each databases after compacting:\n")
        check_storage_size(client)

        print("\n\nThe compact job has been completed successfully!")

    except Exception as err:
        print('-------------------------------------------------------------------------')
        logging.exception(err)
        print('-------------------------------------------------------------------------')        
        raise err

def single_host_compact_mongodb(host, replicaset, username, password, mongo_auth_mechanism, mongo_uri):

    try:

        # Connection to the replicaset
        client = MongoClient(mongo_uri)
        print(f"Client: {client}")
        
        # Print storage size values of each DB before compacting
        print("Storage size of each databases before compacting:\n")
        check_storage_size(client)

        check_mongodb_health(client)
        single_node_client = MongoClient(f"mongodb://{username}:{password}@{host}/?directConnection=true&authMechanism={mongo_auth_mechanism}")
        print(f"[ {time.strftime('%x %X %Z')} ] - Compacting single node ({host})")
        for db in single_node_client.list_databases():
            if db["name"] not in ["admin", "local", "config"]:
                print(f"[ {time.strftime('%x %X %Z')} ] - ** Database {db['name']} being compacted now **")
                db = single_node_client[db["name"]]
                for collection in db.list_collection_names():
                    try:
                        result = db.command({"compact": collection})
                        print(f"[ {time.strftime('%x %X %Z')} ] - {collection}@{host} : {result}")
                    except OperationFailure as e:
                        print(f"[ {time.strftime('%x %X %Z')} ] - Skipping compact for {collection} on {host}: {e}")
        print(f"-------------------------------------------------------------------------\n")
        
        print(f"[ {time.strftime('%x %X %Z')} ] - Waiting 30 secs...")
        time.sleep(30)
        
        print(f"[ {time.strftime('%x %X %Z')} ] - Checking the node health status...")
        check_mongodb_health(client)

        # Print storage size values of each DB after compacting
        print("Storage size of each databases after compacting:\n")
        check_storage_size(client)

        print("\n\nThe compact job on a single host has been completed successfully!")

    except Exception as err:
        print('-------------------------------------------------------------------------')
        logging.exception(err)
        print('-------------------------------------------------------------------------')        
        raise err

def check_mongodb_health(client):

    # Check if all nodes are healthy to proceed with compacting
    while True:
        status = client.get_database("admin").command("replSetGetStatus")
        all_nodes_ready = True
        for member in status["members"]:
            if member["stateStr"] not in ["PRIMARY", "SECONDARY"]:
                all_nodes_ready = False
                print(f"[ {time.strftime('%x %X %Z')} ] - All nodes haven't reached the healthy status yet. Waiting 5 seconds more...")
                break
        if all_nodes_ready:
            break
        else:
            time.sleep(5)

    print(f"[ {time.strftime('%x %X %Z')} ] - All nodes are healthy!\n")

def check_storage_size(client):

    total_storage_size = 0
    print(f"Client: {client}")
    db_names = client.list_database_names()
    for db_name in db_names:
        db = client[db_name]
        stats = db.command("dbstats")
        # Convert the storage size from bytes to MB
        storage_size_gb = stats["storageSize"] / (1024 * 1024)
        total_storage_size += storage_size_gb
        print(f"Storage size for '{db_name}': {storage_size_gb:.2f} MB")
    print(f"Total storage size': {total_storage_size:.2f} MB")
    print(f"-------------------------------------------------------------------------\n")