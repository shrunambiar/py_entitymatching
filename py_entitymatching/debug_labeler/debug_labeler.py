# coding=utf-8
import pandas as pd
from sklearn.cross_validation import KFold, cross_val_score

import py_entitymatching.catalog.catalog_manager as cm
import py_entitymatching.utils.catalog_helper as ch
import py_entitymatching.utils.generic_helper as gh

from py_entitymatching.feature.autofeaturegen import get_features_for_matching
from py_entitymatching.feature.extractfeatures import extract_feature_vecs
from py_entitymatching.matcher.rfmatcher import RFMatcher
from py_entitymatching.matcherselector.mlmatcherselection import get_xy_data

def _check_function(row, actual_label, pred_label, prob_nonmatch, prob_match,
                    prob_label):
    if row[actual_label] == 0 and row[pred_label] == 1:
        row[prob_label] = row[prob_match]
    elif  row[actual_label] == 1 and row[pred_label] == 0:
        row[prob_label] = row[prob_nonmatch]
    return row




def debug_labeler(labeled_data, exclude_attrs, target_attr, k=5,
                  predict_col='predicted', pred_prob_col='prediction_prob',
                  actual_label_col = 'actual_label',
                  random_state=None):
    # Validate input parameters

    # # We expect the input candset to be of type pandas DataFrame.
    if not isinstance(labeled_data, pd.DataFrame):
        logger.error('Input cand.set is not of type dataframe')
        raise AssertionError('Input cand.set is not of type dataframe')

    if not ch.check_attrs_present(labeled_data, exclude_attrs):
        logger.error('The exclude attrs. are not present in the input '
                     'dataframe')
        raise AssertionError('The exclude attrs. are not present in the input '
                     'dataframe')

    if not ch.check_attrs_present(labeled_data, target_attr):
        logger.error('The target attr is not present in the input dataframe')
        raise AssertionError('The target attr is not present in the input '
                             'dataframe')

        # Do metadata checking
        # # Mention what metadata is required to the user
    ch.log_info(logger, 'Required metadata: cand.set key, fk ltable, '
                        'fk rtable, '
                        'ltable, rtable, ltable key, rtable key', verbose)

    # # Get metadata
    ch.log_info(logger, 'Getting metadata from catalog', verbose)

    key, fk_ltable, fk_rtable, ltable, rtable, l_key, r_key = \
        cm.get_metadata_for_candset(
            labeled_data, logger, verbose)

    # # Validate metadata
    ch.log_info(logger, 'Validating metadata', verbose)
    cm._validate_metadata_for_candset(labeled_data, key, fk_ltable, fk_rtable,
                                      ltable, rtable, l_key, r_key,
                                      logger, verbose)

    proj_ltable =  ltable[gh.list_diff(list(ltable.columns), [em.get_key(
        ltable)])]
    proj_rtable =  rtable[gh.list_diff(list(rtable.columns), [em.get_key(
        rtable)])]
    feature_table = get_features_for_matching(proj_ltable, proj_rtable)
    feature_vectors = extract_feature_vecs(labeled_data, feature_table=feature_table,
                                            attrs_after=target_attr,
                                              show_progress=False)
    folds = KFold(len(labeled_data), n_folds=k, shuffle=True,
                  random_state=random_state)

    list_prediction_dfs = []

    for train_indices, pred_indices in folds:
        rf = RFMatcher()
        train = feature_vectors.iloc[train_indices]
        test = feature_vectors.iloc[pred_indices]
        label_test = labeled_data.iloc[pred_indices]
        rf.fit(table=train, exclude_attrs=exclude_attrs,
               target_attr=target_attr)
        preds = rf.predict(table=test, exclude_attrs=exclude_attrs,
                           target_attr=predict_col)
        X, Y = get_xy_data(x=None, y=None, table=test,
                           exclude_attrs=exclude_attrs, target_attr=target_attr)
        predict_probs = rf.clf.predict_proba(X)
        label_test = label_test.copy()
        # label_test[pred_prob_col] = -1
        # label_test[pred_prob_col+'_nonmatch']
        label_test.insert(1, pred_prob_col, -1)
        label_test.insert(2, actual_label_col, label_test[target_attr])
        label_test.insert(3, predict_col, preds)
        label_test.insert(4, pred_prob_col + '_nonmatch', predict_probs[:, 0])
        label_test.insert(5, pred_prob_col + '_match', predict_probs[:, 1])
        label_test = label_test[label_test[actual_label_col != predict_col]]
        label_test = label_test.apply(_check_function, axis=1)
        list_prediction_dfs.append(label_test)
    concatenated_dfs = pd.concat([list_prediction_dfs])
    cm.copy_properties(labeled_data, concatenated_dfs)



