"""
Estimate P(E|e_i+1) of ranking entities in row population

author: Shuo Zhang
"""
from row_evaluation import Row_evaluation
from elastic import Elastic
import json
import math


class P_e_e(Row_evaluation):
    def __init__(self, index_name="table_index", lamda=0.5):
        """

        :param index_name: name of index
        :param lamda: smoothing parameter
        """
        super().__init__()
        self.__lambda = lamda
        self.__tes = Elastic(index_name)
        self.__elas = Elastic("dbpedia_2015_10")
        f = open("similarity_jaccard_validation.json", "r")
        self.__similarity = json.load(f)

    def estimate_pee_load(self, cand, seed, n):
        """Load json ll and similarity"""
        p_all = {}
        for entity in cand:
            n_e = n[entity]["n_seed"]
            n_e_i = n[entity]["n_e_1"]
            n_e_e = n[entity]["n_seed_e"]
            sim = self.similarity_load(entity, seed)
            if n_e_i == 0:
                p_all[entity] = 0
            elif n_e == 0:
                p_all[entity] = (1 - self.__lambda) * sim  # /n_e_i
            else:
                p_all[entity] = ((self.__lambda * (n_e_e / n_e) + (1 - self.__lambda) * sim))  # /n_e_i
        return p_all

    def estimate_pee(self, cand, seed, test_val):
        """Estimate P(c|e_i+1) for candidates"""
        p_all = {}
        body = self.generate_search_body(seed)
        n_e = self.estimate_length(body)
        for entity in cand:
            body = self.generate_search_body([entity])
            n_e_i = self.estimate_length(body)  # number of tables containing e_i+1
            seed_e = []
            seed_e.append(entity)
            for en in seed:
                seed_e.append(en)
            body = self.generate_search_body(seed_e)
            n_e_e = self.estimate_length(body)  # number of tables containing e_i+1 and E
            sim = self.similarity_load(entity, seed)
            if n_e_i == 0:
                p_all[entity] = 0
            elif n_e == 0:
                p_all[entity] = (1 - self.__lambda) * sim  # /n_e_i
            else:
                p_all[entity] = ((self.__lambda * (n_e_e / n_e) + (1 - self.__lambda) * sim))  # /n_e_i
        return p_all

    def estimate_length(self, body):
        """Search body, return the number of hits containg body"""
        try:
            res = self.__tes.search_complex(body).keys()
            table_ids = self.exclude_test_val(res, test_val)
            n = len(table_ids)
        except:
            n = 0
        return n

    def similarity_load(self, e, seed):  # Load similarity from json
        sim = 0
        for entity in seed:
            sim += max(self.__similarity.get(entity + "-" + e, 0), self.__similarity.get(e + "-" + entity, 0))
        return sim / len(seed)

    def similarity(self, e, seed):  # WLM computes similarity between two entities
        sim = 0
        entity1 = "<dbpedia:" + e + ">"
        try:
            doc1 = self.__elas.get_doc(entity1)
            en_set1 = doc1.get("_source").get("related_entity_names")
        except:  # entity exception:not exist
            en_set1 = []
        for entity in seed:
            sim += self.sim_e_e(en_set1, entity)
        return sim / len(seed)

    def sim_e_e(self, en_set1, e2):  # WLM using outlink instead of inlink
        entity2 = "<dbpedia:" + e2 + ">"
        try:
            doc2 = self.__elas.get_doc(entity2)
            en_set2 = doc2.get("_source").get("related_entity_names")
        except:
            en_set2 = []
        cap = []
        for en in set(en_set1 + en_set2):
            if en in en_set1 and en in en_set2:
                cap.append(en)
        max_l = max(len(en_set1), len(en_set2))
        min_l = min(len(en_set1), len(en_set2))
        E_l = 4000000
        if max_l == 0 or len(cap) == 0:
            score = 0
        else:
            score = 1 - (math.log(max_l) - math.log(len(cap))) / (math.log(E_l) - math.log(min_l))
        return score

    def exclude_test_val(self, table_ids, test_val):
        """Exclude test set and validation set"""
        tables = []
        for table_id in table_ids:
            if table_id not in test_val:
                tables.append(table_id)
        return tables

    def generate_search_body(self, seed):
        """Generate and return search body"""
        body = {}
        if len(seed) == 1:  # One constraints
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {"entities_1st_col": seed[0]}
                        }
                    }
                }
            }
        else:  # Multiple constraints
            must = []
            must.append({"match": {"entities_1st_col": seed[0]}})
            for item in seed[1:]:
                must.append({"match_phrase": {"entities_1st_col": item}})
            body = {
                "query": {
                    "bool": {
                        "must": must
                    }
                }
            }
        return body


if __name__ == "__main__":
    # ----------------test---similarity--------------#
    # test = P_e_e()
    # e = "Audi_A4"
    # seed = ["Audi_A6","Audi_A8"]
    # l = ["Tons","Registry (flag)"]
    # p = test.similarity(e, seed)
    # print(p)
    # ----------------test all------------------#
    test = P_e_e()
    cand = ["Audi_A6", "Audi_A8", "Audi_A4L"]
    seed = ["Audi_A4"]
    test_val = []
    p = test.estimate_pee(cand, seed, test_val)
    print(p)
    #
    # def filter_query_2(self, entity, label):
    #     body = {
    #                     "query": {
    #                         "bool": {
    #                             "must": [
    #                                 {
    #                                     "match": {"entities_1st_col": entity}
    #                                 },
    #                                 {
    #                                     "match_phrase": {"entities_1st_col": label}
    #                                 }
    #                             ]
    #                         }
    #                     }}
    #     return body
