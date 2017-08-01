from row_evaluation import Row_evaluation
from row_re_pee import P_e_e
from ap_rr import Ap_Rr
import json

if __name__ == "__main__":
    f = open("test_tables_lable_validation.json", "r")
    tables = json.load(f)
    f1 = open("./first_step_results/test_cand_validation.json", "r")
    candis = json.load(f1)  # Candidates filtered by first step
    f2 = open("./second_step/ground_truth_first_validation.json", "r")
    gt_all = json.load(f2)

    result = {}

    f3 = open("table_id_label.json")
    test1 = json.load(f3)
    f2 = open("table_id_lable_validation.json")
    val = json.load(f2)
    test_val = test1 + val

    f4 = open("./second_step/pee_n_exclude_validation.json", "r")
    N = json.load(f4)

    count = 0
    example = P_e_e(lamda=0)
    eval = Row_evaluation()
    Ap = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    Rr = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for key in tables.keys():
        count += 1
        result[key] = {}
        print("-------", key, count, count)
        current_table = tables[key]
        for i in range(1, 6):
            seed, gt = eval.get_seed_gt(i, current_table)
            cand = candis[key][str(i)]
            n = N[key][str(i)]
            p = example.estimate_pee_load(cand, seed, n)
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

    print(Ap)
    print(Rr)


    f2 = open("./second_step/PEE_jaccard_validation.json", "w")
    json.dump(result, f2, ensure_ascii=False)
