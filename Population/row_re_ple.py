"""
Estimate P(L|e_i+1) of ranking entities in row population

author: Shuo Zhang
"""
from row_evaluation import Row_evaluation
from elastic import Elastic
from elastic_cache import ElasticCache
import math
import json


class P_l_e(Row_evaluation):
    def __init__(self, index_name="table_index", lamda=0.5):
        """

        :param index_name: name of index
        :param lamda: smoothing parameter
        """
        super().__init__()
        self.__lambda = lamda
        self.__tes = Elastic(index_name)
        self.__tces = ElasticCache(index_name)
        self.__mu = 2000

        # f = open("./second_step/PLE_vali_p_lm.json", "r")
        # self.p_all_p = json.load(f)


    def estimate_ple(self, cand, l, test_val):
        """Estimate P(l|e_i+1) for candidates"""
        p_all = {}
        for entity in cand:
            p_all[entity] = 0
            for label in l:
                body = self.generate_search_body([entity])
                n_e, _ = self.estimate_length(body)  # number of tables containing e_i+1
                body2 = self.generate_search_body([entity, label])
                n_l_e, table_ids = self.estimate_length(body2)  # number of tables containing e_i+1&label
                table_ids_exclude = self.exclude_test_val(table_ids, test_val)  # exclude test&vali set from table KB
                p_l_theta = self.p_l_theta_lm_cache(label, table_ids_exclude)
                if n_e == 0:
                    p_all[entity] += self.__lambda * p_l_theta
                else:
                    p_all[entity] += self.__lambda * p_l_theta + (1 - self.__lambda) / len(l) * n_l_e / n_e
        return p_all


    def estimate_ple_store(self, cand, l, test_val):
        """Estimate P(l|e_i+1) for candidates"""
        p_all = {}
        p_all_n = {}
        for entity in cand:
            p_all[entity] = {}
            p_all_n[entity] = {}
            for label in l:
                body = self.generate_search_body([entity])
                n_e, _ = self.estimate_length(body)  # number of tables containing e_i+1
                body2 = self.generate_search_body([entity, label])
                n_l_e, table_ids = self.estimate_length(body2)  # number of tables containing e_i+1&label
                table_ids_exclude = self.exclude_test_val(table_ids, test_val)  # exclude test&vali set from table KB
                p_l_theta = self.p_l_theta_lm_cache(label, table_ids_exclude)
                p_all[entity][label] = p_l_theta
                if n_e == 0:
                    p_all_n[entity][label]= 0
                else:
                    p_all_n[entity][label] = n_l_e/(n_e*len(l))

        return p_all,p_all_n

    def estimate_ple_load(self, cand, l, test_val, p_all_n):
        """Estimate P(l|e_i+1) for candidates"""

        p_all = {}
        for entity in cand:
            p_all[entity] = 0
            for label in l:
                #p_l_theta = p_all_p[entity][label]
                p_all[entity] += (1 - self.__lambda) * p_all_n[entity][label]
                #p_all[entity] += self.__lambda * p_l_theta #+ (1 - self.__lambda)*self.p_all_n[entity][label]
        return p_all

    def estimate_length(self, body):
        """Search body, return the number of hits containing body"""
        try:
            res = self.__tes.search_complex(body).keys()
            n = len(res)
        except:
            res = {}
            n = 0
        return n, res

    def p_l_theta_lm_cache(self, label, table_ids2):
        """Using language modeling estimate P(l|theta), with ElasticCache instead of Elastic"""
        p_label = self.parse(label)
        p_l_theta = 0
        c_l = self.__tces.coll_length("headings")  # collection length
        for t in p_label:
            try:
                a_t = self.__tes.analyze_query(t)
            except:
                continue
            l_l = 0  # table label length(table containing t)
            t_f = 0  # tf of label
            c_tf = self.__tces.coll_term_freq(a_t, "headings")  # tf in collection
            for table_id in table_ids2:
                l_l += self.__tces.doc_length(table_id, "headings")
                t_f += self.__tces.term_freq(table_id, "headings", a_t)
            try:
                p = (t_f + self.__mu * c_tf / c_l) / (l_l + self.__mu)
                p_l_theta += math.log(p)
            except:
                p_l_theta += 0

        if p_l_theta != 0:
            p_l_theta = math.exp(p_l_theta)
        return p_l_theta

    def p_l_theta_lm(self, label, table_ids2):
        """Using language modeling estimate P(l|theta)"""
        p_label = self.parse(label)
        p_l_theta = 0
        c_l = self.__tes.coll_length("headings")  # collection length
        for t in p_label:
            a_t = self.__tes.analyze_query(t)
            l_l = 0  # table label length(table containing t)
            t_f = 0  # tf of label
            c_tf = self.__tes.coll_term_freq(a_t, "headings")  # tf in collection
            for table_id in table_ids2:
                l_l += self.__tes.doc_length(table_id, "headings")
                t_f += self.__tes.term_freq(table_id, "headings", a_t)
            try:
                p = (t_f + self.__mu * c_tf / c_l) / (l_l + self.__mu)
                p_l_theta += math.log(p)
            except:
                p_l_theta += 0

        if p_l_theta != 0:
            p_l_theta = math.exp(p_l_theta)
        return p_l_theta

    def p_l_theta(self, label, table_ids2):
        """Estimate P(l|theta)"""
        p_label = self.parse(label)
        p_l_theta = 0
        for t in p_label:
            a_t = self.__tes.analyze_query(t)
            l_l = 0
            t_f = 0
            for table_id in table_ids2:
                l_l += self.__tes.doc_length(table_id, "headings")
                t_f += self.__tes.term_freq(table_id, "headings", a_t)
            try:
                p_l_theta += math.log(t_f / l_l)
            except:  # t_f or l_l is 0
                p_l_theta += 0
        if p_l_theta != 0:
            p_l_theta = math.exp(p_l_theta)
        return p_l_theta

    def generate_search_body(self, query):
        """Generate and return search body"""
        body = {}
        if len(query) == 1:
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {"entities_1st_col": query[0]}
                        }
                    }
                }
            }
        elif len(query) == 2:
            body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {"entities_1st_col": query[0]}
                            },
                            {
                                "match_phrase": {"headings": query[1]}
                            }
                        ]
                    }
                }}
        return body


if __name__ == "__main__":
    # ----------------test-----------------#
    test = P_l_e(index_name="table_toy")
    cand = ["[SS_Exact|SS Exact]"]
    l = ["Tons", "Registry (flag)"]
    test_val = []
    p = test.estimate_ple(cand, l, test_val)
    print(p)
