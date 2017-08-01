"""
Evaluation of Column Population
-------------------------------

Column population performance evaluation.

@author: Shuo Zhang
"""

from ap_rr import Ap_Rr
from elastic import Elastic


class Column_evaluation(object):
    def __init__(self, test_tables=None):
        """

        :param test_tables: 1000 wiki test tables
        """
        self.test_tables = test_tables
        self.__tes = Elastic("table_index_label")

    def rank_candidates(self, cand, seed, e_gt, c=None, E=None):
        """

        :param cand: candidate entities
        :param seed: Seed entity
        :param c: Table caption
        :return: Ranked suggestions
        """
        pass

    def find_candidates_table(self, seed, c, test_val, num=100):
        """Using table_index and table caption to find candidate labels"""
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
            labels = doc["_source"]["headings"]
            for entity in labels:
                if entity in seed:
                    continue
                if entity not in cand:
                    cand.append(entity)
        return cand

    def find_candidates_table_seed(self, seed, test_val, num=100):
        """Using 'table_index' and seed label to find candidate labels"""
        cand = []
        for label in seed:
            try:
                a_label = self.__tes.analyze_query(label)
                res = self.__tes.search(query=a_label, field="headings", num=num)
            except:
                res = {}
            for table_id in res.keys():
                if table_id in test_val:
                    continue
                doc = self.__tes.get_doc(table_id)
                labels = doc["_source"]["headings"]
                for l in labels:
                    if l in seed:
                        continue
                    if l not in cand:
                        cand.append(l)
        return cand


    def find_candidates_table_entity(self, seed, E, test_val, num=100):
        """Using 'table_index' and entities to find candidate labels"""
        cand = []
        for entity in E:
            try:
                res = self.__tes.search(query=entity, field="entities_1st_col", num=num)
            except:
                res = {}
            for table_id in res.keys():
                if table_id in test_val:
                    continue
                doc = self.__tes.get_doc(table_id)
                labels = doc["_source"]["headings"]
                for l in labels:
                    if l in seed:
                        continue
                    if l not in cand:
                        cand.append(l)
        return cand

    def get_entity(self, table):
        """Get all entities in first column"""
        all_entity = []
        for item in table["data"]:
            data = item[0].split("[")[1].split("|")[0]
            all_entity.append(data)
        return all_entity

    def get_caption(self, table):
        """Get table caption"""
        return table["caption"]


    def get_labels(self, i, table):
        "Get table headings in a list"
        return table["title"][:i], table["title"][i:]

    def get_labels_replace(self, i, table):
        """Get table headings with entity replaced by string:[A|B] by B"""
        return label_replace(table["title"][:i]),label_replace(table["title"][i:])

    def column_evaluation(self):
        """

        :return: MAP, MRR for different number of seed entities
        """
        MAP = {}
        MRR = {}
        for i in range(1, 6):
            sum_ap = 0
            sum_rr = 0
            test_val = []
            for table in self.test_tables.values():
                seed, e_gt = self.get_labels(i, table)  # seed entities; ground truth
                c = self.get_caption(table)  # table caption
                E = self.get_entity(table)
                cand = self.find_candidates_table(seed, c, E, test_val)
                r = self.rank_candidates(cand, seed, e_gt, c=c, E=E)  # ranked suggestions
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

    def exclude_test_val(self, table_ids, test_val):
        """Exclude test set and validation set"""
        tables = []
        for table_id in table_ids:
            if table_id not in test_val:
                tables.append(table_id)
        return tables

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
        out = {}
        for key in table.keys():
            out[key] = table_ids[key]
        return out

    def exclude_test_val(self, table_ids, test_val):
        tables = []
        for table_id in table_ids:
           if table_id not in test_val:
               tables.append(table_id)
        return tables

def label_replace(caption):
    label_return = []
    for cap in caption:
        if "[" in cap and "|" in cap and "]" in cap:
            entity_str = cap.split("|")[1].split("]")[0]
        elif "*" in cap:
            entity_str = cap.replace("*","")
        else:
            entity_str = cap
        label_return.append(entity_str)
    return label_return

def main():
    test_tables = tables
    eval = Column_evaluation()
    for table_id, table in test_tables.items():
        print(eval.get_caption(table))
        print(eval.get_entity(table))
        print(eval.get_labels(2, table))


if __name__ == "__main__":
    main()
