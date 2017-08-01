"""
This is the baseline of column population
"""

from Column_rank_label import Rank_label
from elastic import Elastic
from ap_rr import Ap_Rr
import json
from Norm_string import normalization


class rank_baseline(Rank_label):
    def __init__(self):
        super().__init__()
        self.__tes = Elastic("table_index_label_both")
        self.__num = 1000

    def rank_candidates_baseline(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(res_e_exclude + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl_baseline(all_table, seed_label, E)
        print("111")
        for label in cand:
            p_all[label] = 0
            cs = self.label_score(seed_label, label, test_vali)
            for table in all_table:
                table_label = headings.get(table, [])
                if label in table_label:
                    p_all[label] += p_t_ecl[table] * cs
        return p_all

    def p_t_ecl_baseline(self, all_table, seed_label, E):

        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            #sim_l = self.label_score_all(seed_label, table_label, test_vali)
            p[table] = max(sim_e, 0.000001) #* max(sim_l, 0.000001)
        return p, headings

    def rank_candidates_baseline2(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(res_e_exclude + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl_baseline(all_table, seed_label, E)
        print("111")
        for label in cand:
            p_all[label] = 0
            cs = self.label_score(seed_label, label, test_vali)
            for table in all_table:
                table_label = headings.get(table, [])
                if label in table_label:
                    p_all[label] += p_t_ecl[table] * cs
        return p_all

    def p_t_ecl_baseline2(self, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            sim_l = self.overlap(table_label, seed_label)
            #sim_l = self.label_score_all(seed_label, table_label, test_vali)
            p[table] = max(sim_e, 0.000001) * max(sim_l, 0.000001)
        return p, headings

    def rank_candidates_baseline3(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        try:
            res_c = self.__tes.search(c, field="caption", num=self.__num)  # search tables with similar caption
        except:
            res_c = {}
        res_c_exclude = self.exclude_test_val_dict(res_c, test_vali)  # exclude test_val sets
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(res_e_exclude + list(res_c_exclude.keys()) + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            #cs = self.label_score(seed_label, label, test_vali)
            for table in all_table:
                table_label = headings.get(table, [])
                if label in table_label:
                    cs = self.label_score(table_label, label, test_vali)
                    p_all[label] += p_t_ecl[table] * cs
        return p_all

    def rank_candidates_baseline4(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        try:
            res_c = self.__tes.search(c, field="caption", num=self.__num)  # search tables with similar caption
        except:
            res_c = {}
        res_c_exclude = self.exclude_test_val_dict(res_c, test_vali)  # exclude test_val sets
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(res_e_exclude + list(res_c_exclude.keys()) + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            cs = self.label_score(seed_label, label, test_vali)
            for table in all_table:
                table_label = headings.get(table, [])
                if label in table_label:
                    p_all[label] += p_t_ecl[table] * (0.5*cs+0.5)
        return p_all

    def rank_candidates_baseline5(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        for label in cand:
            cs = self.label_score(seed_label, label, test_vali)
            p_all[label] = cs
        return p_all

    def label_score_all(self, seed_label, table_label, test_vali):
        score = 0
        for l in table_label:
            if l not in seed_label:
                tmp = self.label_score(seed_label, l, test_vali)
                if tmp > score:
                    score = tmp
        return score

    def label_score(self, seed_label, label, test_vali):
        score = 0
        for l in seed_label:
            if l != label:
                body = self.generate_search_body2([l])
                n1 = self.__tes.search_complex(body, num=self.__num).keys()
                n1_exclude = self.exclude_test_val(n1, test_vali)
                if len(n1_exclude) != 0:
                    body2 = self.generate_search_body2([l, label])
                    n2 = self.__tes.search_complex(body2, num=self.__num).keys()
                    n2_exclude = self.exclude_test_val(n2, test_vali)
                    score += len(n2_exclude) / len(n1_exclude)
                else:
                    score += 0
        return score / len(seed_label)

    def estimate_length(self, body, test_val):
        """Search body, return the number of hits containg body"""
        try:
            res = self.__tes.search_complex(body).keys()
            table_ids = self.exclude_test_val(res, test_val)
            n = len(table_ids)
        except:
            n = 0
        return n

    def generate_search_body2(self, query):
        """Generate and return search body"""
        body = {}
        if len(query) == 1:
            body = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {"headings_nor": query[0]}
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
                                "match": {"headings_nor": query[0]}
                            },
                            {
                                "match_phrase": {"headings_nor": query[1]}
                            }
                        ]
                    }
                }}
        return body


if __name__ == "__main__":
    print("-------------This is used for testing--------------")
    a = rank_baseline()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    f1 = open("./column_first_step_label/column_test_cand_label.json", "r")
    cand_all = json.load(f1)
    f2 = open("column_test_ids.json", "r")
    cand_id = json.load(f2)
    f3 = open("column_validation_ids.json", "r")
    vali_id = json.load(f3)
    test_vali = list(set(cand_id + vali_id))
    Ap = {1: 0, 2: 0, 3: 0}
    Rr = {1: 0, 2: 0, 3: 0}
    count = 1
    result = {}
    for key in tables.keys():
        print(key, "---", count, count)
        count += 1
        curren_table = tables[key]
        result[key] = {}
        for i in range(1, 4):
            cand = cand_all[key][str(i)]
            l_i, gt = a.get_labels(i, curren_table)
            cand = normalization(cand)
            l_i = normalization(l_i)
            gt = normalization(gt)
            c = a.get_caption(curren_table)
            E = a.get_entity(curren_table)
            p = a.rank_candidates_baseline(cand, l_i, gt, c=c, E=E, test_vali=test_vali)
            result[key][str(i)] = p
            p = sorted(p.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p:
                r.append(item[0])
            _, _, ap, rr = Ap_Rr(r, gt)
            Ap[i] += ap
            Rr[i] += rr
        print(Ap)
        print(Rr)


