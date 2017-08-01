"""Column first step, use only caption

not use anymore!!!!
"""
from column_evaluation import Column_evaluation
import json


def store_gt():
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    gt_all = {}
    for key in tables.keys():
        gt_all[key] = {}
        current_table = tables[key]
        eval = Column_evaluation(test_tables=current_table)
        for i in range(1, 4):
            _, gt = eval.get_labels(i, current_table)
            gt_all[key][str(i)] = gt

    f1 = open("column_gt_test_first.json", "w")
    json.dump(gt_all, f1, indent=2)


def caption():
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    f1 = open("column_test_ids.json")
    test = json.load(f1)
    f2 = open("column_validation_ids.json")
    val = json.load(f2)
    test_val = test + val
    print(len(test_val))
    candidate = {}
    for num in [256]:
        print(num, num, num)
        for key in tables.keys():
            candidate[key] = {}
            current_table = tables[key]
            eval = Column_evaluation(test_tables=current_table)
            c = eval.get_caption(current_table)  # "House of Representatives"
            for i in range(1, 4):
                seed, gt = eval.get_labels(i, current_table)
                cand = eval.find_candidates_table(seed, c, test_val, num=num)
                candidate[key][i] = cand
        f1 = open("./column_first_step_results/C_test_" + str(num) + ".json", "w")
        json.dump(candidate, f1, ensure_ascii=False)


def use_label():
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    f1 = open("column_test_ids.json")
    test = json.load(f1)
    f2 = open("column_validation_ids.json")
    val = json.load(f2)
    test_val = test + val
    print(len(test_val))
    candidate = {}
    for num in [256]:
        print(num, num, num)
        for key in tables.keys():
            candidate[key] = {}
            current_table = tables[key]
            eval = Column_evaluation(test_tables=current_table)
            for i in range(1, 4):
                seed, gt = eval.get_labels(i, current_table)
                cand = eval.find_candidates_table_seed(seed, test_val, num=num)
                candidate[key][i] = cand
        f1 = open("./column_first_step_results/L_test_" + str(num) + ".json", "w")
        json.dump(candidate, f1, ensure_ascii=False)


def use_entity():
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    f1 = open("column_test_ids.json")
    test = json.load(f1)
    f2 = open("column_validation_ids.json")
    val = json.load(f2)
    test_val = test + val
    print(len(test_val))
    candidate = {}
    for num in [64]:
        print(num, num, num)
        for key in tables.keys():
            candidate[key] = {}
            current_table = tables[key]
            eval = Column_evaluation(test_tables=current_table)
            for i in range(1, 4):
                seed, gt = eval.get_labels(i, current_table)
                E = eval.get_entity(current_table)
                cand = eval.find_candidates_table_entity(seed, E, test_val, num=num)
                candidate[key][i] = cand
        f1 = open("./column_first_step_results/E_test_" + str(num) + ".json", "w")
        json.dump(candidate, f1, ensure_ascii=False)


if __name__ == "__main__":
    store_gt()
    # caption()
    # use_label()
#use_entity()
