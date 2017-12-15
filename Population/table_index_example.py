"""
An example indexer for tables.

author: Shuo Zhang

table example
"table-0003-724": {
    "data": [
      [ "1996", "There's a Girl in Texas", "20", "2014", "33"],
      [ "1996", "[Every_Light_in_the_House|Every Light in the House]", "3", "78", "10"],
      [ "1997", "[(This_Ain't)_No_Thinkin'_Thing|(This Ain't) No Thinkin' Thing]", "1", "2014", "1"],
      [ "1997", "[I_Left_Something_Turned_On_at_Home|I Left Something Turned On at Home]", "2", "2014", "1"],
      [ "\"\u2014\" denotes releases that did not chart", "\"\u2014\" denotes releases that did not chart", "\"\u2014\" denotes releases that did not chart", "\"\u2014\" denotes releases that did not chart", "\"\u2014\" denotes releases that did not chart"]
    ],
    "entity": ["Every_Light_in_the_House", "(This_Ain't)_No_Thinkin'_Thing", "I_Left_Something_Turned_On_at_Home"]
    "heading": ["Year", "Single", "Peak chart positions", "Peak chart positions", "Peak chart positions"],
    "caption": "Singles",
    "pgTitle": "xxx"
  },

"""
from elastic import Elastic
import json


def table_index():
    index_name = "table_index_frt"
    mappings = {
        "entity_n": Elastic.notanalyzed_field(),
        "entity": Elastic.analyzed_field(),
        "data": Elastic.analyzed_field(),
        "caption": Elastic.analyzed_field(),
        "headings_n": Elastic.notanalyzed_field(),
        "headings": Elastic.analyzed_field(),
        "pgTitle": Elastic.analyzed_field(),
        "catchall": Elastic.analyzed_field(),
    }
    elastic = Elastic(index_name)
    elastic.create_index(mappings, force=True)
    tables = {}  # todo: map ur data into a json; see above
    docs = {}
    for table_id, table in tables.items():
        caption = table.get("caption")
        headings = label_replace(table.get("heading"))
        pgTitle = table.get("pgTitle")
        entity = table.get("entity")
        data = table.get("data")
        catcallall = " ".join([caption, json.dumps(data), pgTitle, headings])
        docs[table_id] = {
            "entity_n": entity,
            "entity": entity,
            "data": data,
            "caption": caption,
            "headings_n": headings,
            "headings": headings,
            "pgTitle": pgTitle,
            "catchall": catcallall
        }
    elastic.add_docs_bulk(docs)


def parse(h):
    """entity [A|B]----B"""
    if "[" in h and "|" in h and "]" in h:
        return h.split("|")[1].split("]")[0]
    else:
        return h


def label_replace(headings):
    """Only keep entity strings"""
    return [parse(i) for i in headings]


if __name__ == "__main__":
    table_index()
