from row_evaluation import Row_evaluation
from row_re_pce3 import P_c_e
from ap_rr import Ap_Rr
import json

if __name__ == "__main__":
    f = open("test_tables_lable.json", "r")
    tables = json.load(f)
    f1 = open("./second_step/test_cand.json", "r")
    candis = json.load(f1)  # Candidates filtered by first step
    result = {}
    example = P_c_e(lamda=0.5)
    f3 = open("table_id_label.json")
    test1 = json.load(f3)
    f2 = open("table_id_lable_validation.json")
    val = json.load(f2)
    test_val = test1 + val
    count = 1
    keys = []
    eval = Row_evaluation()
    Ap = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    Rr = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for key in tables.keys():
        keys.append(key)
        result[key] = {}
        print("-------", key, count, count)
        count += 1
        current_table = tables[key]
        c = eval.get_caption(current_table)  # "House of Representatives"
        for i in range(1, 6):
            _, gt = eval.get_seed_gt(i, current_table)
            cand = candis[key][str(i)]
            p = example.estimate_pce(cand, c, test_val)
            result[key][str(i)] = p
            p1 = sorted(p.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p1:
                r.append(item[0])
            _, _, ap, rr = Ap_Rr(r, gt)
            Ap[i] += ap
            Rr[i] += rr
        print(Ap)
        print(Rr)

        f2 = open("./second_step/PCE_lm.json", "w")
        json.dump(result, f2, ensure_ascii=False)
