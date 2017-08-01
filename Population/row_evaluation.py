"""
Evaluation of Row Population
----------------------------

Row population performance evaluation.

@author: Shuo Zhang
"""

from sparql_wapper import virtuoso_sparql
from ap_rr import Ap_Rr
from elastic import Elastic


class Row_evaluation(object):
    def __init__(self, index_name="dbpedia_2015_10_type_cat", url="<http://dbpedia.org>", test_tables=None):
        """

        :param index_name: name of index
        :param url: http://dbpedia.org in gustav
        :param test_tables: 1000 wiki test tables
        """
        self.__index_name = index_name
        self.__elastic = Elastic(self.__index_name)
        self.__tes = Elastic("table_index")
        self.__url = url
        self.test_tables = test_tables

    def rank_candidates(self, cand, seed, e_gt, c=None, a=None):
        """

        :param cand: candidate entities
        :param seed: Seed entity
        :param a: Attributes
        :param c: Table caption
        :return: Ranked suggestions
        """
        pass

    def find_candidates_table(self, seed, c, test_val, num=100):
        """Using 'table_index' and table caption to find candidate entities"""
        cand = []
        if len(c) == 0:
            res = {}
        else:
            aquery = self.__tes.analyze_query(c)
            res = self.__tes.search(query=aquery, field="caption", num=num)
        for table_id in res.keys():
            if table_id in test_val:  # exclude test and validation tables
                continue
            doc = self.__tes.get_doc(table_id)
            entities = doc["_source"]['entities_1st_col']
            for entity in entities:
                # entity = entity.split("<dbpedia:")[1].split(">")[0]
                if entity in seed:
                    continue
                if entity not in cand:
                    cand.append(entity)
        return cand

    def find_candidates_table_onlyseed(self, seed, c, test_val, num=100):
        """Using 'table_index' and caption with seed to find candidate entities"""
        cand = []

        for en in seed:
            try:
                res = self.__tes.search(query=en, field="entities_1st_col", num=num)
            except:
                res = {}
            for table_id in res.keys():
                if table_id in test_val:  # exclude test and validation tables
                    continue
                doc = self.__tes.get_doc(table_id)
                entities = doc["_source"]["entities_1st_col"]
                for entity in entities:
                    if entity in seed:
                        continue
                    if entity not in cand:
                        cand.append(entity)
        # print("len",len(cand))
        return cand

    def find_candidates_table_seed(self, seed, c, test_val, num=100):
        """Using 'table_index' and caption with seed to find candidate entities"""
        cand = []
        if len(c) == 0:
            res = {}
        else:
            aquery = self.__tes.analyze_query(c)
            res = self.__tes.search(query=aquery, field="caption", num=num)
        for table_id in res.keys():
            if table_id in test_val:  # exclude test and validation tables
                continue
            doc = self.__tes.get_doc(table_id)
            entities = doc["_source"]['entities_1st_col']
            for entity in entities:
                # entity = entity.split("<dbpedia:")[1].split(">")[0]
                if entity in seed:
                    continue
                if entity not in cand:
                    cand.append(entity)

        for en in seed:
            try:
                res = self.__tes.search(query=en, field="entities_1st_col", num=num)
            except:
                res = {}
            for table_id in res.keys():
                if table_id in test_val:  # exclude test and validation tables
                    continue
                doc = self.__tes.get_doc(table_id)
                entities = doc["_source"]["entities_1st_col"]
                for entity in entities:
                    if entity in seed:
                        continue
                    if entity not in cand:
                        cand.append(entity)
        # print("len",len(cand))
        return cand

    def find_candidates_cat_type_a(self, seed, field, num=100, a=None, c=None):  # only category
        """Using seed entities' analyzed category and type to find candidates"""
        cate_candidates = []
        category = []
        for entity in seed:
            en_id = "<dbpedia:" + entity + ">"
            try:
                doc = self.__elastic.get_doc(en_id)
                cats = doc.get("_source").get(field)
                for cat in cats:
                    if cat not in category:
                        category.append(cat)
            except:  # ID not exists in index
                print("------", entity)

        for cat in category:
            try:
                res = self.__elastic.search(query=cat, field=field, num=num)
            except:
                res = {}
                print("EXCEPTION:", cat)
            for entity in res.keys():
                en_id = entity.split("<dbpedia:")[1].split(">")[0]
                if en_id in seed:
                    continue
                if en_id not in cate_candidates:
                    cate_candidates.append(en_id)
        # print("len",len(cate_candidates))
        return cate_candidates

    def find_candidates_cat_type(self, seed, field, num=100, a=None, c=None):  # only category
        """Using seed entities' notanalyzed category and type to find candidates"""
        cate_candidates = []
        category = []
        for entity in seed:
            en_id = "<dbpedia:" + entity + ">"
            try:
                doc = self.__elastic.get_doc(en_id)
                cats = doc.get("_source").get(field)
                for cat in cats:
                    if cat not in category:
                        category.append(cat)
            except:  # ID not exists in index
                print("------", entity)

        for cat in category:

            body = {
                "query": {
                    "constant_score": {
                        "filter": {
                            "term": {
                                field: cat
                            }
                        }
                    }
                }
            }
            res = self.__elastic.search_complex(body=body, num=num)

            for entity in res.keys():
                en_id = entity.split("<dbpedia:")[1].split(">")[0]
                if en_id in seed:
                    continue
                if en_id not in cate_candidates:
                    cate_candidates.append(en_id)
        return cate_candidates

    def find_candidates(self, seed, method, a=None, c=None):
        """"Given seed entities, using virtuoso return candidate entities"""
        cat_pred = ""
        if method == 1:  # category
            cat_pred = "<http://purl.org/dc/terms/subject>"
        elif method == 2:  # type
            cat_pred = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        cate_union = []  # or string
        for entity in seed:  # get category union
            en_url = "<http://dbpedia.org/resource/" + entity + ">"  # e.g. <http://dbpedia.org/resource/Air_Atlanta_Icelandic>"
            sparql_query = "{}{}{}{}{}{}".format("select ?o from ", self.__url, " where {", en_url, cat_pred, " ?o}")
            results = virtuoso_sparql(sparql_query=sparql_query)
            for result in results:
                o = result.get('o', None).get('value', None)
                if o not in cate_union:
                    cate_union.append(o)
        cand = []
        for category in cate_union:  # using category to get all entities
            try:
                category = "<" + category + ">"
                sparql_query = "{}{}{}{}{}{}".format("select ?s from ", self.__url, " where { ?s ", cat_pred, category,
                                                     "}")
                results = virtuoso_sparql(sparql_query=sparql_query)
            except:
                results = {}
            for result in results:
                s = result.get('s', None).get('value', None)
                entity = s.split("/resource/")[1]
                if entity in seed:
                    continue
                if entity not in cand:
                    cand.append(entity)
        return cand  # Charles_Plott

    def get_seed_gt(self, i, table):
        """Get seed entities and ground truth entities in lists"""
        all_entity = []
        for item in table["data"]:
            data = item[0].split("[")[1].split("|")[0]
            all_entity.append(data)
        return all_entity[0:i], all_entity[i:]

    def get_attributes(self, table):
        """Get attributes of seed table"""
        attribute = []
        for item in table["data"]:
            attribute += item[1:]
        return attribute

    def get_caption(self, table):
        """Get table caption"""
        return table["caption"]

    def get_headings(self, table):
        "Get table headings in a list"
        return table["title"]

    def row_evaluation(self):
        """

        :return: MAP, MRR for different number of seed entities
        """
        MAP = {}
        MRR = {}
        for i in range(1, 6):
            sum_ap = 0
            sum_rr = 0
            for table in self.test_tables.values():
                seed, e_gt = self.get_seed_gt(i, table)  # seed entities; ground truth
                a = self.get_attributes(table)  # attributes
                c = self.get_caption(table)  # table caption
                cand = self.find_candidates(seed, a, c)
                r = self.rank_candidates(cand, seed, e_gt, c=c, a=a)  # ranked suggestions
                _, _, ap, rr = Ap_Rr(r, e_gt)
                sum_ap += ap
                sum_rr += rr
            MAP[i] = sum_ap / len(self.test_tables)
            MRR[i] = sum_rr / len(self.test_tables)
        return MAP, MRR

    def plot(self):
        """plot map,mrr VS i"""
        pass

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

    def exclude_test_val_dict(self, table_ids, test_val):
        """Exclude test set and validation set"""
        table = dict.fromkeys(table_ids)
        for table_id in test_val:
            table.pop(table_id, None)
        return table.keys()

    def exclude_test_val_dict(self, table_ids, test_val):
        """Exclude test set and validation set"""
        for table_id in test_val:
            table_ids.pop(table_id, None)
        return table_ids

    def exclude_test_val(self, table_ids, test_val):
        tables = []
        for table_id in table_ids:
           if table_id not in test_val:
               tables.append(table_id)
        return tables


def main():
    test_tables = {}
    eval = Row_evaluation(test_tables=test_tables)
    MAP, MRR = eval.row_evaluation()
    print("Plot:", MAP, MRR)


if __name__ == "__main__":
    main()
