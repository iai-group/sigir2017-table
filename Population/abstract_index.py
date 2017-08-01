"""
This script is used to index dbpedia abstract:
id: <dbpedia:sth>
abstract: analyzed abstract

author: Shuo Zhang
"""

from elastic import Elastic
import os
import json

def abstract_index():
    index_name = "dbpedia_2015_10_abstract"
    mappings = {
        "abstract":Elastic.analyzed_field(),
    }
    elastic = Elastic(index_name)
    elastic.create_index(mappings, force=True)
    maindir = "/data/scratch/tmp/long_abstracts_en.ttl"
    f = open(maindir,"r")
    docs = {}
    count = 1
    for line in f:
        if "started" in line or "completed" in line:
            continue
        tmp = line.strip().split(" ",2)
        entity_id = "<dbpedia:"+tmp[0].split("<http://dbpedia.org/resource/")[1].split(">")[0]+">"
        abstract = tmp[2].split('"')[1]
        docs[entity_id] = {"abstract":abstract}
        if len(docs) == 10000:
            print(count, count, count)
            elastic.add_docs_bulk(docs)
            docs = {}
            count += 1
    elastic.add_docs_bulk(docs)


if __name__ == "__main__":
    abstract_index()
