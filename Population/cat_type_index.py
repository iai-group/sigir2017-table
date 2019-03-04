"""
This script is used to index dbpedia category and types information
id:<dbpedia:sth>
  type_n: not analyzed type
  type_a: analyzed type
  cat_n: not analyzed category
  cat_a: analyzed category
Type only include ontology types.

author: Shuo Zhang
"""

from elastic import Elastic
import json
import re

def convert_from_camelcase(name):
    """Splits a CamelCased string into a new one, capitalized, where words are separated by blanks.

    :param name:
    :return:
    """
    # http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).replace("_", " ")#.capitalize()

def extrac_type():
    out = open("entity_type.json", "w")
    dir = "/data/scratch/tmp/instance_types_transitive_en.ttl"
    f = open(dir, "r")
    entity_type = {}
    for line in f:
        if "started" in line:  # first line
            continue
        tmp = line.strip().split()
        try:
            entity = tmp[0].split("resource/")[1].split(">")[0]
            type = tmp[2]
            print("entity:", entity, "...Type:", type)
            if entity not in entity_type.keys():
                entity_type[entity] = []
                entity_type[entity].append(type)
            else:
                entity_type[entity].append(type)
        except:  # last line
            print(line)
    print(len(entity_type))
    json.dump(entity_type, out, indent=2)


def extrac_cat():
    out = open("entity_category.json", "w")
    dir = "/data/scratch/tmp/article_categories_en.ttl"
    f = open(dir, "r")
    entity_type = {}
    for line in f:
        if "started" in line:  # first line
            continue
        try:
            tmp = line.strip().split()
            entity = tmp[0].split("resource/")[1].split(">")[0]
            cat = tmp[2].split("/Category:")[1].split(">")[0]
            print("entity:", entity, "...cat:", cat)
            if entity not in entity_type.keys():
                entity_type[entity] = []
                entity_type[entity].append(cat)
            else:
                entity_type[entity].append(cat)
        except:  # last line
            print(line)
    print(len(entity_type))
    json.dump(entity_type, out, indent=2)


def cat_type_index():
    f1 = open("entity_category.json", "r")
    entity_cat = json.load(f1)
    f2 = open("entity_type.json", "r")
    entity_type = json.load(f2)
    index_name = "dbpedia_2015_10_type_cat"
    mappings = {
        "type_n": Elastic.notanalyzed_field(),
        "type_a": Elastic.analyzed_field(),
        "category_n": Elastic.notanalyzed_field(),
        "category_a": Elastic.analyzed_field()
    }
    elastic = Elastic(index_name)
    elastic.create_index(mappings, force=True)
    keys = list(set(list(entity_cat.keys()) + list(entity_type.keys())))
    docs = {}
    count = 1
    for key in keys:
        entity = "<dbpedia:" + key + ">"
        type_tmp = entity_type.get(key, [])
        type = []
        for t in type_tmp:
            if t.startswith("<http://dbpedia.org/ontology"): # only keep ontology type
                tmp = t.split(">")[0].rsplit("/")[-1]
                type.append(tmp)

        cat = entity_cat.get(key, [])
        cat_a = []
        for c in cat:  # prepare analyzed version
            cat_a.append(c.replace("_", " "))
        type_a = []
        for t in type:
            type_a.append(convert_from_camelcase(t))  # e.g., camelcase "MeanOfTransportation" => "Mean Of Transportation"

        # print('TTTT',type)
        doc = {"type_n": type, "type_a": type_a, "category_n": cat, "category_a": cat_a}
        docs[entity] = doc
        if len(docs) == 10000:
            print("-------", count)
            count += 1
            elastic.add_docs_bulk(docs)
            docs = {}
    elastic.add_docs_bulk(docs)
    print("Finish now")

def statistic():
    a = 0
    b = 0
    f1 = open("entity_category.json", "r")
    entity_cat = json.load(f1)
    f2 = open("entity_type.json", "r")
    entity_type = json.load(f2)
    keys = list(set(list(entity_cat.keys()) + list(entity_type.keys())))
    for key in keys:
        type_tmp = entity_type.get(key, [])
        type = []
        for t in type_tmp:
            if t.startswith("<http://dbpedia.org/ontology"):  # only keep ontology type
                tmp = t.split(">")[0].rsplit("/")[-1]
                type.append(tmp)
                b += 1

        cat = entity_cat.get(key, [])
        cat_a = []
        for c in cat:  # prepare analyzed version
            cat_a.append(c.replace("_", " "))
            a += 1
    print("Finish now")
    print(a,b,len(keys))


if __name__ == "__main__":
    # extrac_type()
    # extrac_cat()
    # cat_type_index()
    statistic()
    # a = "<http://dbpedia.org/ontology/Location>"
    # print(a)
    # tmp = a.split(">")[0].rsplit("/")[-1]
    # print(tmp)
    # ---------------Testing-----------------
    # index_name = "dbpedia_2015_10_type_cat"
    # es = Elastic(index_name)
    # entity_id = "<dbpedia:Audi_A4>"
    # field = "type_a"
    # doc = es.get_doc(entity_id, field)
    # cats = doc.get("_source").get(field)
    # print("TYPE:",cats)
    # for cat in cats:
    #     cat = "Scranton/Wilkes-Barre_RailRiders_players"
    #     cat = es.analyze_query(cat)
    #     print(cat)
    #     res = es.search(query=cat, field=field, num=100)
    #     print(res.keys())
    #     break
    # name = "Ase Bsef Cfds Dfdls"
    # a = convert_from_camelcase(name)
    # print(a)
    # f2 = open("entity_type.json", "r")
    # entity_type = json.load(f2)
    # print(entity_type["Audi_A4"])

