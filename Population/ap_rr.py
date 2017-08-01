"""
This file is used to evaluate AP, RR, DCG given results list and gt list
"""

import math
def Ap_Rr(r, e_gt):
    gt = e_gt
    ranking = r

    p5, p10, ap, rr, num_rel = 0, 0, 0, 0, 0

    for i, doc_id in enumerate(ranking):
        if doc_id in gt:  # doc is relevant
            num_rel += 1
            pi = num_rel / (i + 1)  # P@i
            ap += pi  # AP

            if i < 5:  # P@5
                p5 += 1
            if i < 10:  # P@10
                p10 += 1
            if rr == 0:  # Reciprocal rank
                rr = 1 / (i + 1)

    p5 /= 5
    p10 /= 10
    ap /= len(gt)  # divide by the number of relevant documents
    return round(p5, 3),round(p10, 3),round(ap, 3),round(rr, 3)

def dcg(rel, p):
    dcg = rel[0]
    for i in range(1, min(p, len(rel))):
        dcg += rel[i] / math.log(i + 1, 2)  # rank position is indexed from 1..
    return dcg

def DCG(ranking, e_gt):
    gt = e_gt
    gains = []  # holds corresponding relevance levels for the ranked docs
    for doc_id in ranking:
        gain = gt.get(doc_id, 0)
        gains.append(gain)
    #print("\tGains:", gains)

    # relevance levels of the idealized ranking
    gain_ideal = sorted([v for _, v in gt.items()], reverse=True)
    #print("\tIdeal gains:", gain_ideal)

    ndcg5 = dcg(gains, 5) / dcg(gain_ideal, 5)
    ndcg10 = dcg(gains, 10) / dcg(gain_ideal, 10)


    #print("\tNDCG@5:", round(ndcg5, 3), "\n\tNDCG@10:", round(ndcg10, 3))
    return round(ndcg5, 3),round(ndcg10, 3)

def gt_relevence(gt):
    """Give gt relevence scores from 1-3"""
    l = len(gt)
    gt_rel = {}
    count = 1
    for item in gt:
        if count < l/3:
            gt_rel[item] = 3
        elif count < 2*l/3:
            gt_rel[item] = 2
        else:
            gt_rel[item] = 1
        count += 1
    return gt_rel


if __name__ == "__main__":
    r = [1, 2, 4, 5, 3, 6, 9, 8, 10, 7,8,8,8,8,8,8,8]
    gt = [1, 3]
    print(Ap_Rr(r,gt))
    gt = {1: 2, 2: 1}
    print(DCG(r,gt))
    print(gt_relevence(r))


