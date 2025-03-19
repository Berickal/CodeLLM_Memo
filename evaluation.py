import textdistance as td
import numpy as np
from rouge_score import rouge_scorer
from tqdm import tqdm
import json
import os
from utils import get_data, clean_code

def perf_data(ref : str, gen : list, metric : str = 'levenshtein'):
    rs = []
    ref = clean_code(ref)
    for g in gen:
        g = clean_code(g)
        if metric == 'levenshtein' :
            rs.append(td.levenshtein.normalized_similarity(g, ref))
        elif metric == 'cosine':
            rs.append(td.cosine.normalized_similarity(g, ref))
        elif metric == 'ncd':
            rs.append(td.zlib_ncd.normalized_similarity(g, ref))
        elif metric == 'rouge':
            scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
            scores = scorer.score(ref, g)
            rs.append(scores['rouge1'].precision)
    return np.mean(np.asarray(rs))

def perf_file(file, metric : str = 'ncd'):
    data = get_data(file)
    ref, rs = data['ref'] if 'ref' in data.keys() else data['bitflip'][0]['gen'][0], []
    for exp in data['bitflip'] :
        gen = [el.replace(exp['prompt'], '') for el in exp['gen']]
        rs.append(perf_data(ref, gen, metric))
    return rs

def sensitivity_eval(X):
    drop = []
    for idx in range(len(X)-1):
        drop.append(abs(X[idx] - X[idx + 1])) 
    return np.max(drop)

def eval_folder(folder : str, metric : str = 'ncd'):
    files = [pos_json for pos_json in os.listdir(folder) if pos_json.endswith('.json')]
    dist = []
    for f in tqdm(files):
        eval = perf_file(f'{folder}/{f}', metric)
        dist.append(sensitivity_eval(eval))
    return np.asarray(dist)


