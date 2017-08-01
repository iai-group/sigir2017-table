"""
This is used to index labeled and redirect-replaced tables in tables_redi2

"""
from elastic import Elastic
import os
import json
from Norm_string import normalization

def table_index():
    test_file = open("table_id_label.json", "r")
    test_id = json.load(test_file)
    validation_file = open("table_id_lable_validation.json", "r")
    validation_id = json.load(validation_file)
    index_name = "table_index_label_both"
    mappings = {
        "type":Elastic.notanalyzed_field(),
        "entities_1st_col":Elastic.notanalyzed_field(),
        "entities_attr":Elastic.notanalyzed_field(),
        "caption":Elastic.analyzed_field(),
        "headings_nor":Elastic.notanalyzed_field(),
        "headings_n": Elastic.notanalyzed_field()
    }
    elastic = Elastic(index_name)
    elastic.create_index(mappings, force=True)
    maindir = "/data/scratch/smart_table/TableParse/tables_redi2"
    count = 1
    type_count = 1
    type_count2 = 1
    for d in os.listdir(maindir):
        docs = {}
        inpath = os.path.join(maindir,d)
        infile = open(inpath, mode="r", errors="ignore")
        tables = json.load(infile)
        for key in tables.keys():
            if key in test_id:
                print("type-count:",type_count)
                type = "test"
                type_count += 1
            elif key in validation_id:
                print("type-count2222",type_count2)
                type = "validation"
                type_count2 += 1
            else:
                type = "all"
            table = tables[key]
            first_column = []
            attr_entity=[]
            caption = table["caption"]
            headings = label_replace(table["title"])
            headings1 = normalization(headings)
            data = table["data"]
            for row in data:
                if len(row) == 0:
                    continue
                if "[" in row[0]:
                    try:
                        first_column.append(row[0].split("[")[1].split("|")[0])
                    except:
                        pass
                for attr in row[1:]:
                    if "[" in attr:
                        try:
                            attr_entity.append(attr.split("[")[1].split("|")[0])
                        except:
                            print(attr)
            docs[key] = {"type":type,"entities_1st_col":list(set(first_column)),"entities_attr":list(set(attr_entity)),"caption":caption,"headings_nor":headings1,"headings_n":headings}

        elastic.add_docs_bulk(docs)
        print("--------",count,"--------",len(docs))
        count+=1

def label_replace(caption):
    caption_return = []
    for cap in caption:
        if "[" in cap and "|" in cap and "]" in cap:
            entity_str = cap.split("|")[1].split("]")[0]
        elif "*" in cap:
            entity_str = cap.replace("*","")
        else:
            entity_str = cap
        caption_return.append(entity_str)
    return caption_return


if __name__ == "__main__":
    table_index()
    # caption = [ "Athlete", "Country", "1", "2", "3", "4", "Total", "Notes" ]
    # print(caption_replace(caption))
