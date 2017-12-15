"""
Evaluation of Row Population
----------------------------

Row population performance evaluation.

@author: Shuo Zhang
"""

from elastic import Elastic


class Row_evaluation(object):
    def __init__(self, index_name="dbpedia_2015_10_type_cat"):
        """

        :param index_name: name of index
        """
        self.__index_name = index_name
        self.__elastic = Elastic(self.__index_name)
        self.__tes = Elastic("table_index_frt")

    def rank_candidates(self, seed , c=None, l=None):
        """

        :param cand: candidate entities
        :param seed: Seed entity
        :param a: Attributes
        :param c: Table caption
        :return: Ranked suggestions
        """
        pass

    def find_candidates_c(self, seed_E, c, num=100):
        """table caption to find candidate entities"""
        cand = []
        res = self.__tes.search(query=c, field="catchall", num=num)
        for table_id in res.keys():
            doc = self.__tes.get_doc(table_id)
            labels = doc["_source"]["entity"]
            cand += labels
        return set([i for i in cand if i not in seed_E])

    def find_candidates_e(self, seed_E, num=None):
        """seed entities to find candidate entities"""
        cand = []
        for entity in seed_E:
            body = self.generate_search_body(item=entity, field="entity")
            res = self.__tes.search_complex(body=body, num=num)
            for table_id in res.keys():
                doc = self.__tes.get_doc(table_id)
                labels = doc["_source"]["entity"]
                cand += labels
        return set([i for i in cand if i not in seed_E])

    def generate_search_body(self, item, field):
        """Generate search body"""
        body = {
            "query": {
                "bool": {
                    "must": {
                        "term": {field: item}
                    }
                }
            }
        }
        return body

    def find_candidates_cat(self, seed_E, num=100):  # only category
        """return seed entities' categories"""
        cate_candidates = []
        category = []
        for entity in seed_E:
            doc = self.__elastic.get_doc(entity)
            cats = doc.get("_source").get("category")
            category += cats

        for cat in set(category):
            body = self.generate_search_body(item=cat, field="category")
            res = self.__elastic.search_complex(body=body, num=num)
            cate_candidates += [i for i in res.keys() if i not in seed_E]
        return set(cate_candidates)

    def parse(self, text):
        """Put query into a term list for term iteration"""
        stopwords = []
        terms = []
        # Replace specific characters with space
        chars = ["'", ".", ":", ",", "/", "(", ")", "-", "+"]
        for ch in chars:
            if ch in text:
                text = text.replace(ch, " ")
        # Tokenization
        for term in text.split():  # default behavior of the split is to split on one or more whitespaces
            # Stopword removal
            if term in stopwords:
                continue
            terms.append(term)
        return terms
