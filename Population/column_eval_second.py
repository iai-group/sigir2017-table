"""
This file is used to evaluate column second step results.
"""
from Column_rank_label import Rank_label
from ap_rr import Ap_Rr
import json
from Norm_string import normalization

def label_replace(caption):
    """Replace entity label by its string"""
    caption_return = []
    for cap in caption:
        if "[" in cap and "|" in cap and "]" in cap:
            entity_str = cap.split("|")[1].split("]")[0]
        elif "*" in cap:
            entity_str = cap.replace("*","")
        else:
            entity_str = cap
        caption_return.append(entity_str)
    return caption_return
def recall(gt,cand):
    count = 0
    for entity in set(gt):
        if entity in cand:
            count += 1
    return count

def low(sth):
    """Lower case a list"""
    sth_r = []
    for item in sth:
        sth_r.append(item.lower())
    return sth_r

def sig_test():
    """Get all the methods' ap in the same order for significance test"""
    print("-------------This is used for testing--------------")
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    ff = open("./column_second_step/baseline.json", "r")
    result = json.load(ff)
    count = 1
    AP = {}
    RR = {}
    for key in tables.keys():
        print(key, "---", count, count)
        count += 1
        curren_table = tables[key]
        # AP[key] = {}
        # RR[key] = {}
        for i in range(3, 4):
            print(i)
            l_i, gt = a.get_labels(i, curren_table)
            p = result[key][str(i)]
            p = sorted(p.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p:
                r.append(item[0])
            r1 = normalization(r)
            r = []
            for item in r1:
                if item not in r:
                    r.append(item)
            gt = normalization(gt)
            _, _, ap, rr = Ap_Rr(r, gt)
            AP[key] = ap
            RR[key] = rr
    f = open("./sig_test/column_baseline_ap_3.json", "w")
    json.dump(AP, f, ensure_ascii=False, indent=2)
    f = open("./sig_test/column_baseline_rr_3.json", "w")
    json.dump(RR, f, ensure_ascii=False, indent=2)



def eval():
    """Second step MAP MRR evaluation"""
    print("-------------This is used for testing--------------")
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    Ap = {1: 0, 2: 0, 3: 0}
    Rr = {1: 0, 2: 0, 3: 0}
    ff = open("./column_second_step/el_label.json", "r")
    result = json.load(ff)
    count = 1
    for key in tables.keys():
        print(key, "---", count, count)
        count += 1
        curren_table = tables[key]
        for i in range(1, 4):
            l_i, gt = a.get_labels(i, curren_table)
            p = result[key][str(i)]
            p = sorted(p.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p:
                r.append(item[0])
            r1 = normalization(r)
            r = []
            for item in r1:
                if item not in r:
                    r.append(item)
            gt = normalization(gt)
            _, _, ap, rr = Ap_Rr(r, gt)
            Ap[i] += ap
            Rr[i] += rr
        print(Ap)
        print(Rr)

def get_rank():
    """Ranking ap, to see the top and bottom tables(check why they are good or bad)"""
    print("-------------This is used for testing--------------")
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    ff = open("column_try_label.json", "r")
    result = json.load(ff)
    count = 1
    maps = {}
    for key in tables.keys():
        count += 1
        curren_table = tables[key]
        l_i, gt = a.get_labels(3, curren_table)
        p = result[key][str(3)]
        p = sorted(p.items(), key=lambda d: d[1], reverse=True)[:20]
        r = []
        for item in p:
            r.append(item[0])
        _, _, ap, rr = Ap_Rr(r, gt)
        if ap == 1:
            print("gt",gt)
            print("rk",r)
        aa = recall(gt,r)
        maps[key] = ap
    p_top = sorted(maps.items(), key=lambda d: d[1], reverse=True)[:10]
    p_top_return = []
    for item in p_top:
        p_top_return.append(item[0])
    p_last = sorted(maps.items(), key=lambda d: d[1], reverse=True)[-10:]
    p_last_return = []
    for item1 in p_last:
        p_last_return.append(item1[0])
    return p_top_return,p_last_return

def detail():
    """Get all the good an bad tables, separately store their seed label, caption, gt for analysis"""
    p_top, p_last = get_rank()
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    ff = open("column_try_label.json", "r")
    result = json.load(ff)
    count = 0
    detail_top = {}
    for key in p_top:
        detail_top[key] = {}
        count += 1
        curren_table = tables[key]
        l_i, gt = a.get_labels(3, curren_table)
        c = a.get_caption(curren_table)
        p = result[key][str(3)]
        r = []
        p1 = sorted(p.items(), key=lambda d: d[1], reverse=True)[:10]
        count = 0
        for item in p1:
            count+=1
            r.append(item[0])
            if count == 10:
                break
        detail_top[key]["seed_label"] = label_replace(l_i)
        detail_top[key]["ground_truth"] = label_replace(gt)
        detail_top[key]["ranked_list"] = r
        detail_top[key]["caption"] = c
    # f1 = open("column_second_top10.json","w")
    # json.dump(detail_top, f1, indent=2)
    detail_last = {}
    for key in p_last:
        detail_last[key] = {}
        count += 1
        curren_table = tables[key]
        c = a.get_caption(curren_table)
        l_i, gt = a.get_labels(3, curren_table)
        p = result[key][str(3)]
        r = []
        count = 0
        for item in p:
            count+=1
            r.append(item)
            if count == 20:
                break
        detail_last[key]["seed_label"] = label_replace(l_i)
        detail_last[key]["ground_truth"] = label_replace(gt)
        detail_last[key]["ranked_list"] = r
        detail_last[key]["caption"] = c
    f2 = open("column_second_last10.json", "w")
    json.dump(detail_last, f2, indent=2)

def two():
    """Column second step, combine two methods for evaluation"""
    print("-------------This is used for testing--------------")
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    Ap = {1: 0, 2: 0, 3: 0}
    Rr = {1: 0, 2: 0, 3: 0}
    ff = open("./column_second_step/column_all.json", "r")
    result = json.load(ff)
    ff1 = open("./column_second_step/cs.json", "r")
    result1 = json.load(ff1)
    count = 1
    lamda = 1
    for key in tables.keys():
        print(key, "---", count, count)
        count += 1
        curren_table = tables[key]
        for i in range(1, 4):
            l_i, gt = a.get_labels(i, curren_table)
            p1 = {}
            p_n = result[key][str(i)]
            p_sum_n = sum(p_n.values())
            p_nor_n = {}
            for key1, value in p_n.items():  # Normalization
                p_nor_n[key1] = value / p_sum_n
            p_s = result1[key][str(i)]
            p_sum_s = sum(p_s.values())
            p_nor_s = {}
            for key2, value in p_s.items():  # Normalization
                if p_sum_s != 0:
                    p_nor_s[key2] = value / p_sum_s
                else:
                    p_nor_s[key2] = value
            for id in p_n.keys():
                p1[id] = lamda*p_nor_n.get(id, 0)+(1-lamda)*p_nor_s.get(id, 0)
            p = sorted(p1.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p:
                r.append(item[0])
            r = normalization(r)
            gt = normalization(gt)
            _, _, ap, rr = Ap_Rr(r, gt)
            Ap[i] += ap
            Rr[i] += rr
        print(Ap)
        print(Rr)

def plot_pre():
    """get table ap of tables with AP=0,,0.4<AP<0.6,AP=1"""
    print("-------------This is used for testing--------------")
    a = Rank_label()
    f = open("column_test_tables.json", "r")
    tables = json.load(f)
    Ap = {1: 0, 2: 0, 3: 0}
    Rr = {1: 0, 2: 0, 3: 0}
    ff = open("./column_second_step/column_all.json", "r")
    result = json.load(ff)
    count = 1
    ap_all1 = {}
    ap_all2 = {}
    ap_all3 = {}
    bad = []
    for key in tables.keys():
        print(key, "---", count, count)
        count += 1
        curren_table = tables[key]
        for i in range(1, 4):
            l_i, gt = a.get_labels(i, curren_table)
            p = result[key][str(i)]
            p = sorted(p.items(), key=lambda d: d[1], reverse=True)[:1000]
            r = []
            for item in p:
                r.append(item[0])
            # r = normalization(r)
            # gt = normalization(gt)
            _, _, ap, rr = Ap_Rr(r, gt)
            if ap > 0.4 and ap < 0.6:
                bad.append((key,i))
            Ap[i] += ap
            Rr[i] += rr
            if i == 1:
                ap_all1[key] = ap
            elif i == 2:
                ap_all2[key] = ap
            elif i == 3:
                ap_all3[key] = ap
        print(Ap)
        print(Rr)
    re = {}
    re['1'] = ap_all1
    re['2'] = ap_all2
    re['3'] = ap_all3
    # f = open("ap_all.json", "w")
    # json.dump(re, f, ensure_ascii=False)
    f1 = open("middle_table_id.json", "w")
    json.dump(bad, f1, ensure_ascii=False)
    # return ap_all1, ap_all2, ap_all3

import matplotlib.pyplot as plt
def plot():
    """Plot 1000 test tables's AP distribution"""
    f = open("ap_all.json", "r")
    re = json.load(f)
    ap_all1, ap_all2, ap_all3 = re['1'],re['2'],re['3']
    x = [l+1 for l in list(range(1000))]
    y = list(ap_all1.values())
    y2 = list(ap_all2.values())
    y3 = list(ap_all3.values())
    plt.figure(figsize=(6, 2.5))
    plt.plot(x, sorted(y, reverse = True),'b-', label='|L|=1', linewidth=2)
    plt.plot(x, sorted(y2, reverse=True), 'r-', label='|L|=2', linewidth=2)
    plt.plot(x, sorted(y3, reverse=True), 'g-', label='|L|=3', linewidth=2)
    plt.legend(loc=0, prop={'size': 12})
    plt.xlabel('Table')
    plt.ylabel('AP')
    plt.ylim(-0.05, 1.05)
    plt.show()

def sth():
    """Convert ap file into table1:[1,2,3],,,,means tables, when seed number = 1,2,3 AP=..."""
    f = open("middle_table_id.json", "r")
    bad = json.load(f)
    re_bad = {}
    for item in bad:
        if item[0] not in re_bad.keys():
            re_bad[item[0]] = [item[1]]
        else:
            re_bad[item[0]].append(item[1])
    ff = open("middle_id.json","w")
    json.dump(re_bad, ff, ensure_ascii=False)




if __name__ == "__main__":
    # eval()
    # p_top,p_last = get_rank()
    # print(p_top)
    # print(p_last)
    # detail()
    # two()
    # plot_pre()
    plot()
    # sth()
    # sig_test()
