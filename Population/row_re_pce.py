"""
Estimate P(Caption|e_i+1) of ranking entities in row population
Two LM
author: Shuo Zhang
"""
from row_evaluation import Row_evaluation
from elastic import Elastic
import json
import math


class P_c_e(Row_evaluation):
    def __init__(self, lamda=0.5):
        """

        :param lamda: smoothing parameter
        """
        super().__init__()
        self.__lambda = lamda
        self.__elas = Elastic("dbpedia_2015_10_abstract")
        self.__tes = Elastic("table_index")
        self.__mu = 2000

    def estimate_pce(self, cand, c, test_val):
        """Estimate P(c|e_i+1) for candidates"""
        p_all = {}
        caption = self.parse(c)  # Put query into a list
        for entity in cand:
            p = 0
            body = self.generate_search_body(entity)
            _, table_ids = self.estimate_length(body)  # Search table containing entity
            table_ids_exclude = self.exclude_test_val(table_ids, test_val)  # Exclude test&validation
            entity_id = "<dbpedia:" + entity + ">"
            kb_l = self.__elas.doc_length(entity_id, "abstract")  # entity abstract length
            kb_c_l = self.__elas.coll_length("abstract")  # entity abstract collection length
            collection_l = self.__tes.coll_length("caption")  # caption collection length
            for t in caption:  # Iterate term in caption
                term = self.__tes.analyze_query(t)
                c_l, tf = 0, 0  # caption length, term freq
                for table_id in table_ids_exclude:
                    c_l += self.__tes.doc_length(table_id, "caption")  # caption length
                    tf += self.__tes.term_freq(table_id, "caption", term)  # caption term frequency
                tf_c = self.__tes.coll_term_freq(term, "caption")
                kb_tf = self.__elas.term_freq(entity_id, "abstract", term)  # n(t,kb)
                kb_c_tf = self.__elas.coll_term_freq(term, "abstract")  # term freq in kb collection
                p += self.estimate_p(kb_l, kb_tf, kb_c_l, kb_c_tf, tf, c_l, tf_c, collection_l)
            if p != 0:
                p = math.exp(p)
            p_all[entity] = p

        return p_all

    def estimate_p(self, kb_l, kb_tf, kb_c_l, kb_c_tf, tf, c_l, tf_c, collection_l):
        """P(t_c|e_i+1)"""
        p_kb = self.__lambda * (kb_tf + self.__mu * kb_c_tf / kb_c_l) / (kb_l + self.__mu) + (1 - self.__lambda) * (
            tf + self.__mu * tf_c / collection_l) / (c_l + self.__mu)
        if p_kb != 0:
            p_kb = math.log(p_kb)
        return p_kb

    def generate_search_body(self, entity):
        body = {
            "query": {
                "bool": {
                    "must": {
                        "term": {"entities_1st_col": entity}
                    }
                }
            }
        }
        return body

    def estimate_length(self, body):
        """Search body, return the number of hits containing body"""
        try:
            res = self.__tes.search_complex(body, "entities_1st_col").keys()
            n = len(res)
        except:
            res = {}
            n = 0
        return n, res


if __name__ == "__main__":
    cand = ["Abbey_Park_High_School"]
    f1 = open("table_id_label.json")
    test1 = json.load(f1)
    f2 = open("table_id_lable_validation.json")
    val = json.load(f2)
    test_val = test1 + val
    test = P_c_e(lamda=0.5)
    c = "HDSB secondary schools"
    result = test.estimate_pce(cand, c, test_val)
    print(result)
