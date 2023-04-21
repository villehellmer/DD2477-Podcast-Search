# run in terminal before: python -m pip install elasticsearch7
import json
import pprint
from datetime import datetime

try:
    import os
    import sys
    import pandas as pd
    from elasticsearch7 import Elasticsearch
    print("#### All imports loaded succesfully ####")
except Exception as e:
    print("Some modules are missing {}".format(e))

def connect_database():
    es = None
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if es.ping():
        print("#### Connected to the database ####")
    else:
        print("Connection failed")
    return es


def main():
    es = connect_database()
    es.indices.create(index="mydatabase", ignore=400) #CREATE A DATABASE
    json_docs =[]
    f = open('7wdNBT3HNsVEHohuGeSigs.json')
    data = f.read()
    json_data = json.loads(data)
    action = {"index": {"_index": "mydatabase", "_id": 1}}
    json_docs.append(str(action))
    json_docs.append(data)
    #
    # doc = {
    # 'author': 'author_name',
    # 'text': 'Interensting content...',
    # 'timestamp': datetime.now(),
    # }
    doc = json_data
    resp = es.index(index="test-index", id=1, document=doc)

    print(resp['result'])


    #pprint.pprint(json_data)
    #es.bulk("mydatabase", "transcripts", json_docs)
    #print(f)
    #es.indices.delete(index="mydatabase", ignore=[400, 404]) #DELETE A DATABASE
    # res = es.indices.get_alias("*") #get all databases
    # for name in res:
    #     print(name) #print each database

if __name__ == "__main__":
    main()
