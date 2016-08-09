import pandas as pd
import numpy as np
import math

def get_num_positives_tables(ltable, rtable, gold, lid='id', rid='id', fk_ltable_pos=1,
                             fk_rtable_pos=2):
    l_list = list(ltable[lid].values)
    r_list = list(rtable[rid].values)

    l_pos_indices = []
    r_pos_indices = []

    count = 0
    for row in gold.itertuples(index=False):
        if row[fk_ltable_pos] in l_list and row[fk_rtable_pos] in r_list:
            l_pos_indices.append(row[fk_ltable_pos])
            r_pos_indices.append(row[fk_rtable_pos])
            count += 1
    return count, l_pos_indices, r_pos_indices


def get_num_positives_candset(candset, gold, candset_fk_ltable='ltable_id', candset_fk_rtable='rtable_id'):
    c = candset.set_index([candset_fk_ltable, candset_fk_rtable])
    g = gold.set_index([candset_fk_ltable, candset_fk_rtable])
    candset_tuple_ids = list(set(c.index.values).intersection(set(g.index.values)))
    return len(candset_tuple_ids), candset_tuple_ids


def perturb_year(table, indices, max_year, min_year):
    table = table.copy()
    l1 = math.ceil(len(indices)//2)
    up_indices = np.random.choice(indices, l1, replace=False)
    down_indices = list(set(indices).difference(up_indices))
    for i in up_indices:
        print("[index: %s] old: %s" %(i, table.ix[i, 'year']))
        table.ix[i, 'year'] = str(min(max_year, int(table.ix[i, 'year'])+1))
        print("new: %s" %table.ix[i, 'year'])

    for i in down_indices:
        print("[index: %s]Old: %s" %(i, table.ix[i, 'year']))
        table.ix[i, 'year'] = str(max(min_year, int(table.ix[i, 'year'])-1))
        print("New: %s" %table.ix[i, 'year'])
    return table