"""This file is used in column first step to calculate recall(Only use caption or seed+caption)
This is actually used in the paper, cause we replace all the entity label by its string
"""
import json
from Norm_string import normalization


def recall(gt, cand):
    count = 0
    for entity in set(gt):
        if entity in cand:
            count += 1
    return count/len(gt)

def low(sth):
    sth_r = []
    for item in sth:
        sth_r.append(item.lower())
    return sth_r


if __name__ == "__main__":
    gt_file = open("column_gt_vali_first_label.json", "r")
    gt_all = json.load(gt_file)
    for num in [4096]:
        elastic_file = open("L_vali_" + str(num) + ".json", "r")
        elastic_cat_cand = json.load(elastic_file)

        f = open("C_vali_" + str(num) + ".json", "r")
        f_cand = json.load(f)

        f1 = open("E_vali_" + str(num) + ".json", "r")
        f_cand2 = json.load(f1)
        cand_all = {}
        range = ["1", "2", "3"]
        per = {"1": 0, "2": 0, "3": 0}
        gt_len = {"1": 0, "2": 0, "3": 0}
        cand_len = {"1": 0, "2": 0, "3": 0}
        for key in gt_all:
            cand_all[key] = {}
            for item in range:
                gt = gt_all[key][item]

                cand1 = elastic_cat_cand[key][item]
                cand2 = f_cand[key][item]
                cand3 = f_cand2[key][item]
                cand4 = list(set(cand1 + cand2 + cand3))
                cand = []
                for item1 in cand4:
                    if item1 != "":
                        cand.append(item1)

                cand_all[key][item] = cand
                cand_len[item] += len(cand)
                cand_nor = normalization(cand)
                gt_nor = normalization(gt)
                if len(gt_nor) != 0:
                    per[item] += recall(gt_nor, cand_nor)
                    gt_len[item] += len(gt_nor)
                else:
                    per[item] += recall(gt, cand)
                    gt_len[item] += len(gt)
        for key in range:
            per[key] = per[key] / 1000
            cand_len[key] = cand_len[key] / len(gt_all)
        print("-----------NUM-------------",num)
        print(per)
        print(cand_len)
    # f = open("column_test_cand_label.json", "w")
    # json.dump(cand_all, f, ensure_ascii=False)
