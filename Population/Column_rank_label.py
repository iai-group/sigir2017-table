"""
Given seed labels, entities and caption to rank candidate labels.

author: Shuo Zhang
"""

from column_evaluation import Column_evaluation
from elastic import Elastic
from ap_rr import Ap_Rr
from Norm_string import normalization
import json


class Rank_label(Column_evaluation):
    def __init__(self):
        super().__init__()
        self.__tes = Elastic("table_index_label_both")
        self.__num = 1000

    def rank_candidates(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
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
        print(len(res_c_exclude), len(res_e_exclude), len(res_l_exclude), len(all_table))
        p_t_ecl, headings = self.p_t_ecl(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_ce(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        try:
            res_c = self.__tes.search(c, field="caption", num=self.__num)  # search tables with similar caption
        except:
            res_c = {}
        res_c_exclude = self.exclude_test_val_dict(res_c, test_vali)  # exclude test_val sets
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        all_table = set(res_e_exclude + list(res_c_exclude.keys()))
        p_t_ecl, headings = self.p_t_ecl_ce(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_cl(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        try:
            res_c = self.__tes.search(c, field="caption", num=self.__num)  # search tables with similar caption
        except:
            res_c = {}
        res_c_exclude = self.exclude_test_val_dict(res_c, test_vali)  # exclude test_val sets
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(list(res_c_exclude.keys()) + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl_cl(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_el(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = set(res_e_exclude  + res_l_exclude)
        p_t_ecl, headings = self.p_t_ecl_el(all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_e(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        res_e_exclude = self.search_table(E, field="entities_1st_col", test_vali=test_vali)
        all_table = res_e_exclude
        p_t_ecl, headings = self.p_t_ecl_e(all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_c(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        try:
            res_c = self.__tes.search(c, field="caption", num=self.__num)  # search tables with similar caption
        except:
            res_c = {}
        res_c_exclude = self.exclude_test_val_dict(res_c, test_vali)  # exclude test_val sets
        all_table = list(res_c_exclude.keys())
        p_t_ecl, headings = self.p_t_ecl_c(res_c_exclude, all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def rank_candidates_l(self, cand, seed_label, e_gt, c=None, E=None, test_vali=None):
        """Ranking candidate labels"""
        p_all = {}
        res_l_exclude = self.search_table(seed_label, field="headings_nor", test_vali=test_vali)
        all_table = res_l_exclude
        p_t_ecl, headings = self.p_t_ecl_l(all_table, seed_label, E)
        for label in cand:
            p_all[label] = 0
            for table in all_table:
                table_label = headings.get(table,[])
                if label in table_label:
                    p_all[label] += p_t_ecl[table]/len(table_label)
        return p_all

    def p_t_ecl_l(self, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            sim_l = self.overlap(table_label, seed_label)
            p[table] =  max(sim_l, 0.000001)
        return p, headings

    def p_t_ecl_c(self, res_c_exclude, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            p[table] = res_c_exclude.get(table, 0.000001)
        return p, headings

    def p_t_ecl_e(self, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            p[table] = max(sim_e, 0.000001)
        return p, headings

    def p_t_ecl_ce(self, res_c_exclude, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            p[table] = max(sim_e, 0.000001)  * res_c_exclude.get(table, 0.000001)
        return p, headings

    def p_t_ecl_cl(self, res_c_exclude, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            sim_l = self.overlap(table_label, seed_label)
            p[table] = max(sim_l, 0.000001) * res_c_exclude.get(table, 0.000001)
        return p, headings

    def p_t_ecl_el(self, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            sim_l = self.overlap(table_label, seed_label)
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            p[table] = max(sim_e, 0.000001) * max(sim_l, 0.000001)
        return p, headings

    def p_t_ecl(self, res_c_exclude, all_table, seed_label, E):
        p = {}
        headings = {}
        for table in all_table:
            doc = self.__tes.get_doc(table)
            table_label = doc.get("_source").get("headings_nor")
            headings[table] = table_label
            sim_l = self.overlap(table_label, seed_label)
            table_entity = doc.get("_source").get("entities_1st_col")
            sim_e = self.overlap(table_entity, E)
            p[table] = max(sim_e, 0.000001) * max(sim_l, 0.000001) * res_c_exclude.get(table, 0.000001)
        return p, headings

    def search_table_string(self, E, field, test_vali):
        res_e = []
        for element in E:
            try:
                res = self.__tes.search(element, field=field, num=self.__num)
            except:
                res = {}
            for item in res.keys():
                if item not in res_e:
                    res_e.append(item)
        res_e_exclude = self.exclude_test_val(res_e, test_vali)  # exclude test_val sets
        return res_e_exclude

    def search_table(self, E, field, test_vali):
        """Return tables containing any element of E"""
        res_e = []
        for element in E:  # search tables including entity in E
            body = self.generate_search_body(element, field=field)
            res = self.__tes.search_complex(body, num=self.__num)
            if len(res) == 0:
                # try:
                #     a_element = self.__tes.analyze_query(element)
                # except:
                #     a_element = element
                # body = self.generate_search_body(a_element, field=field)
                try:
                    res = self.__tes.search(body,field=field,num=self.__num)
                except:
                    res = {}

            for item in res.keys():
                if item not in res_e:
                    res_e.append(item)
        res_e_exclude = self.exclude_test_val(res_e, test_vali)  # exclude test_val sets
        return res_e_exclude

    def overlap(self, table_entity, seed):
        """Calculate |A and B|/|B|"""
        count = 0
        for label in seed:
            if label in table_entity:
                count += 1
        return count / len(seed)

    def generate_search_body(self, entity, field):
        """Generate search body"""
        body = {
            "query": {
                "bool": {
                    "must": {
                        "term": {field: entity}
                    }
                }
            }
        }
        return body


if __name__ == "__main__":
    print("-------------This is used for testing--------------")
    a = Rank_label()
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
            p = a.rank_candidates(cand, l_i, gt, c=c, E=E, test_vali=test_vali)
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
    ff = open("./column_second_step/column_all_norm.json", "w")
    json.dump(result, ff, ensure_ascii=False)
