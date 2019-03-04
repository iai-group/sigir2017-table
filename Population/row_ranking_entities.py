"""
Estimate P(E|e_i+1) of ranking entities in row population

author: Shuo Zhang
"""

from elastic import Elastic
from row_evaluation import Row_evaluation
from scorer import ScorerLM
import math


class P_e_e(Row_evaluation):
    def __init__(self, index_name="table_index_frt", lamda=0.5):
        """

        :param index_name: name of index
        :param lamda: smoothing parameter
        """
        super().__init__()
        self.__lambda = lamda
        self.index_name = index_name
        self.__tes = Elastic(index_name)
        self.__elas = Elastic("dbpedia_2015_10_abstract")
        self.__mu = 0.5

    def rank_candidates(self, seed, c=None, l=None):
        cand = list(self.find_candidates_e(seed_E=seed, num=1)) + list(self.find_candidates_c(seed_E=seed, c=c)) + list(
            self.find_candidates_cat(seed_E=seed))
        p_all = {}
        pee = self.estimate_pee(cand, seed)
        pce = self.estimate_pce(cand, c)
        ple = self.estimate_ple(cand, l)
        for entity, score in pee.items():
            p_all[entity] = max(0.000001, score) * max(0.000001, pce.get(entity)) * max(0.000001, ple.get(entity))
        return p_all

    def estimate_pee(self, cand, seed):
        """Estimate P(c|e_i+1) for candidates"""
        p_all = {}
        body = self.generate_search_body_multi(seed)
        n_e = self.__tes.estimate_number_complex(body)
        for entity in cand:
            body = self.generate_search_body_multi([entity])
            n_e_i = self.__tes.estimate_number_complex(body)  # number of tables containing e_i+1
            seed_e = []
            seed_e.append(entity)
            for en in seed:
                seed_e.append(en)
            body = self.generate_search_body_multi(seed_e)
            n_e_e = self.__tes.estimate_number_complex(body)  # number of tables containing e_i+1 and E
            sim = 0  # todo
            if n_e_i == 0:
                p_all[entity] = 0
            elif n_e == 0:
                p_all[entity] = (1 - self.__lambda) * sim  # /n_e_i
            else:
                p_all[entity] = ((self.__lambda * (n_e_e / n_e) + (1 - self.__lambda) * sim))  # /n_e_i
        return p_all

    def generate_search_body_multi(self, seed):
        """Generate and return search body"""
        body = {}
        if len(seed) == 1:  # One constraints
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {"entity": seed[0]}
                        }
                    }
                }
            }
        else:  # Multiple constraints
            must = []
            must.append({"match": {"entity": seed[0]}})
            for item in seed[1:]:
                must.append({"match_phrase": {"entity": item}})
            body = {
                "query": {
                    "bool": {
                        "must": must
                    }
                }
            }
        return body

    def estimate_pce(self, cand, c):
        """Estimate P(c|e_i+1) for candidates"""
        p_all = {}
        caption = self.parse(c)  # Put query into a list
        for entity_id in cand:
            p = 0
            body = self.generate_search_body(entity_id, field="entity")
            table_ids = self.__tes.search_complex(body).keys()  # Search table containing entity

            kb_l = self.__elas.doc_length(entity_id, "abstract")  # entity abstract length
            kb_c_l = self.__elas.coll_length("abstract")  # entity abstract collection length
            collection_l = self.__tes.coll_length("caption")  # caption collection length
            for t in caption:  # Iterate term in caption
                term = self.__tes.analyze_query(t)
                c_l, tf = 0, 0  # caption length, term freq
                for table_id in table_ids:
                    c_l += self.__tes.doc_length(table_id, "caption")  # caption length
                    tf += self.__tes.term_freq(table_id, "caption", term)  # caption term frequency
                tf_c = self.__tes.coll_term_freq(term, "caption")
                kb_tf = self.__elas.term_freq(entity_id, "abstract", term)  # n(t,kb)
                kb_c_tf = self.__elas.coll_term_freq(term, "abstract")  # term freq in kb collection
                p += self.estimate_p(kb_l, kb_tf, kb_c_l, kb_c_tf, tf, c_l, tf_c, collection_l)
            if p != 0:
                p = math.exp(p)
            p_all[entity_id] = p
        return p_all

    def estimate_p(self, kb_l, kb_tf, kb_c_l, kb_c_tf, tf, c_l, tf_c, collection_l):
        """P(t_c|e_i+1)"""
        p_kb = self.__lambda * (kb_tf + self.__mu * kb_c_tf / kb_c_l) / (kb_l + self.__mu) + (1 - self.__lambda) * (
            tf + self.__mu * tf_c / collection_l) / (c_l + self.__mu)
        if p_kb != 0:
            p_kb = math.log(p_kb)
        return p_kb

    def estimate_ple(self, cand, l):
        """Estimate P(l|e_i+1) for candidates"""
        p_all = {}
        for entity in cand:
            p_all[entity] = 0
            for label in l:
                body = self.generate_search_body([entity], field="entity")
                n_e = self.__tes.estimate_number_complex(body)  # number of tables containing e_i+1
                body2 = self.generate_search_body_l([entity, label])
                n_l_e = self.__tes.estimate_number_complex(body2)  # number of tables containing e_i+1&label

                p_l_theta = ScorerLM(self.__tes, l, {}).score_doc(table)
                    self.p_l_theta_lm(label, table_ids)
                if n_e == 0:
                    p_all[entity] += self.__lambda * p_l_theta
                else:
                    p_all[entity] += self.__lambda * p_l_theta + (1 - self.__lambda) / len(l) * n_l_e / n_e
        return p_all


    def generate_search_body_l(self, query):
        """Generate and return search body"""
        body = {}
        if len(query) == 1:
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {"entity": query[0]}
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
                                "match": {"entity": query[0]}
                            },
                            {
                                "match_phrase": {"headings_n": query[1]}
                            }
                        ]
                    }
                }}
        return body
