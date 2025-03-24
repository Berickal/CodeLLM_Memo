import sys, os, json, pandas, argparse, logging
from datasets import load_dataset
from tqdm import tqdm
import perturbation as p

def save_data(data, output):
    with open(output, 'w') as f:
        json.dump(data, f)


##----------------------------Code Synthesis Benchmark------------------------##

def load_xlcost(output):
    subsets = ["C++-program-level", "Python-program-level", "Java-program-level", "Javascript-program-level", "Csharp-program-level", "C++-program-level",
         "PHP-program-level", "C++-snippet-level", "Python-snippet-level", "Java-snippet-level", "Javascript-snippet-level", "Csharp-snippet-level", "C++-snippet-level",
         "PHP-snippet-level"]
    df = pandas.DataFrame()
    for fol in subsets:
        ds = load_dataset("codeparrot/xlcost-text-to-code", fol, split="train")
        df_ = ds.to_pandas()
        df_ = df_[df_['text'].str.len() > 150]
        df_ = df_.sample(50, ignore_index=True)
        df = pandas.concat([df, df_], ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['text'], 'ref' : row['code'], 'pert' : p.pertubation_nl(row['text'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')


def load_code_contest(output):
    ds = load_dataset("deepmind/code_contests", split='train')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    # Fix it - There are different language here
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['text'], 'ref' : row['code'], 'pert' : p.pertubation_nl(row['text'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')


def load_apps(output):
    ds = load_dataset("codeparrot/apps", split='train')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['question'], 'ref' : json.loads(row['solutions'])[0], 'pert' : p.pertubation_nl(row['question'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')


def load_mbpp(output):
    ds = load_dataset("mbpp", split='train')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['text'], 'ref' : row['code'], 'pert' : p.pertubation_nl(row['text'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_lbpp(output):
    ds = load_dataset("CohereForAI/lbpp", split='test')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['instruction'], 'ref' : row['completion'], 'pert' : p.pertubation_nl(row['instruction'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_human_eval(output):
    ds = load_dataset("openai/openai_humaneval", split='test')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['prompt'], 'ref' : row['canonical_solution'], 'pert' : p.pertubation_nl(row['prompt'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')


##----------------------------Vulnerabilities Detection Benchmark------------------------##

def load_vuldetect(output):
    #Don't forget the credit
    df = pandas.read_json('./raw/VulDetectBench.jsonl', lines=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['code'], 'pert' : p.pertubation_code(row['text'], language='c', max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_cve_fixes(output):
    ds = load_dataset("euisuh15/cveFixes1")
    folder = ["c", "java", "python"]
    df = pandas.DataFrame()
    for fol in folder:
        ds = load_dataset("euisuh15/cveFixes1", split=fol)
        df_ = ds.to_pandas()
        df_['lang'] = fol
        df = pandas.concat([df, df_], ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['func_before'], 'pert' : p.pertubation_code(row['func_before'], row['lang'], 5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_vulnpatchpairs(output):
    df = pandas.read_json('./raw/VulnPatchPairs.jsonl', lines=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['code'], 'pert' : p.pertubation_code(row['text'], language='c', max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_diversevul(output):
    ds = load_dataset("claudios/DiverseVul", split='test')
    df = ds.to_pandas()
    df = df[df['target'] == 1].sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['prompt'], 'ref' : row['message'], 'pert' : p.pertubation_code(row['prompt'], language='c', max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_devign(output):
    ds = load_dataset("DetectVul/devign", split='train')
    df = ds.to_pandas()
    df = df[df['target'] == True].sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        data = {'text' : row['func'], 'pert' : p.pertubation_code(row['prompt'], language='c', max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_reveal(output):
    return None

##----------------------------Program Repair Benchmark------------------------##
def load_defects4j(output):
    return None


def load_condefect(output):
    ds = load_dataset("xin1997/condefects-python_all_only_input", split="train")
    df = ds.to_pandas()
    for idx, row in tqdm(df.iterrows()):
        code = p.pertubation_code(row['prompt'], language='c', max_pert=5)
        buggy_code, fixed_code = [], []
        for c in code:
            l_ = c['prompt'].splitlines()[0]
            buggy_code.append(l_ + c.split(l_)[1])
            fixed_code.append(c['prompt'].replace(buggy_code, ''))
        data = {'text' : buggy_code[0]['prompt'], 'ref' : fixed_code[0]['prompt'], 'pert' : buggy_code}
        save_data(data)

def load_quixbugs_pr(output):
    ds = load_dataset("Muennighoff/quixbugs", split='train')
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        lang = 'python' if 'def ' in row['buggy_program'] else 'java'
        data = {'text' : row['buggy_program'], 'ref' : row['solution'], 'pert' : p.pertubation_code(row['prompt'], language=lang, max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')


##----------------------------Code Summarization Benchmark------------------------##

def load_codesearchnet(output):
    ds = load_dataset("code-search-net/code_search_net", split="train")
    df = ds.to_pandas()
    df_python = df[df['language'] == 'python']
    df_java = df[df['language'] == 'java']
    df_js = df[df['language'] == 'javascript']
    df_all = pandas.concat([df_python, df_java, df_js], ignore_index=True)
    df_all = df_all.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df_all.iterrows()):
        data = {'text' : row['func_code_string'], 'ref' : row['func_documentation_string'], 'pert' : p.pertubation_code(row['prompt'], language=row['language'], max_pert=5)}
        save_data(data, f'{output}/sample_{idx}.json')

def load_tlcodesum(output):
    return None

##----------------------------Test Generation------------------------##
def load_testeval(output):
    df = pandas.read_json("raw/TestEval.jsonl'") 
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        pert = p.pertubation_code(row['python_solution'], language='python', max_pert=5)
        for p_ in pert:
            fn = p.func_name(p_['prompt'])
            p_['prompt'] = p.build_test_prompt(fn, p_['prompt'], row['description'])
        data = {'text' : row['python_solution'], 'pert' : pert}
        save_data(data, f'{output}/sample_{idx}.json')

def load_bigcodebench(output):
    ds = load_dataset("bigcode/bigcodebench", split="v0.1.0_hf")
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        pert = p.pertubation_code(row['complete_prompt'] + row['canonical_solution'], language='python', max_pert=5)
        for p_ in pert:
            fn = p.func_name(p_['prompt'])
            p_['prompt'] = p.build_test_prompt(fn, p_['prompt'], row['instruct_prompt'])
        data = {'text' : row['complete_prompt'] + row['canonical_solution'], 'ref' : row['test'], 'pert' : pert}
        save_data(data, f'{output}/sample_{idx}.json')


def load_quixbugs_tg(output):
    ds = load_dataset("Muennighoff/quixbugs", split="train")
    df = ds.to_pandas()
    df = df.sample(frac=1, ignore_index=True)
    for idx, row in tqdm(df.iterrows()):
        lang = 'python' if 'def ' in row['solution'] else 'java'
        pert = p.pertubation_code(row['solution'], language=lang, max_pert=5)
        for p_ in pert:
            fn = p.func_name(p_['prompt'])
            p_['prompt'] = p.build_test_prompt(fn, p_['prompt'], row['description'])
        data = {'text' : row['solution'], 'pert' : pert}
        save_data(data, f'{output}/sample_{idx}.json')


def load_code_synthesis(output : str):
    load_xlcost(f'{output}/xlcost/')
    load_apps(f'{output}/apps/')
    load_human_eval(f'{output}/human_eval/')
    load_code_contest(f'{output}/codecontest/')
    load_lbpp(f'{output}/lbpp/')
    load_mbpp(f'{output}/mbpp/')

def load_vulnerability_detection(output : str):
    load_vulnpatchpairs(f'{output}/vulpatchpairs/')
    load_vuldetect(f'{output}/vuldetect/')
    load_devign(f'{output}/devign/')
    load_reveal(f'{output}/reveal/')
    load_diversevul(f'{output}/diversevul/')
    load_cve_fixes(f'{output}/cve_fixes/')

def load_program_repair(output : str):
    load_quixbugs_pr(f'{output}/quixbugs/')
    load_defects4j(f'{output}/defects4j/')
    load_condefect(f'{output}/condefect/')

def load_code_summarization(output : str):
    load_codesearchnet(f'{output}/codesearchnet/')
    load_tlcodesum(f'{output}/tlcodesum/')

def load_test_generation(output : str):
    load_testeval(f'{output}/testeval/')
    load_bigcodebench(f'{output}/bigcodebench/')
    load_quixbugs_tg(f'{output}/quixbugs/')


def load_by_dataset(dataset : str, output : str):
    if dataset == 'xlcost':
        load_xlcost(output)
    elif dataset == 'human_eval':
        load_human_eval(output)
    elif dataset == 'lbpp':
        load_lbpp(output)
    elif dataset == 'mbpp':
        load_mbpp(output)
    elif dataset == 'codecontest':
        load_code_contest(output)
    elif dataset == 'apps':
        load_apps(output)


    elif dataset == 'test_eval':
        load_testeval(output)
    elif dataset == 'bigcodebench':
        load_bigcodebench(output)
    elif dataset == 'bigcodebench':
        load_bigcodebench(output)


    elif dataset == 'cve_fixes':
        load_cve_fixes(output)
    elif dataset == 'vulnpatchpair':
        load_vulnpatchpairs(output)
    elif dataset == 'vuldetectbench':
        load_vuldetect(output)
    elif dataset == 'diversevul':
        load_diversevul(output)
    elif dataset == 'devign':
        load_devign(output)
    elif dataset == 'reveal':
        load_reveal(output)

    elif dataset == 'quixbugs_pr':
        load_quixbugs_pr(dataset)
    elif dataset == 'defects4j':
        load_defects4j(output)
    elif dataset == 'condefects':
        load_condefect(output)

    elif dataset == 'codesearchnet':
        load_codesearchnet(output)
    elif dataset == 'tl_codesum':
        load_tlcodesum(output)


def load(dataset, task, output):
    if(dataset == None and task == None):
        logging.warning("Missing parameters")

    elif task in ["cg", "code_synthesis"]:
        load_code_synthesis(output)

    elif task in ["vd", "vulnerability_detection"]:
        load_vulnerability_detection(output)

    elif task in ["pr", "program_repair"]:
        load_program_repair(output)

    elif task in ["cs", "code_summarization"]:
        load_code_summarization(output)

    elif task in ["tg", "test_generation"]:
        load_test_generation(output)

    elif dataset != None:
        load_by_dataset(dataset, output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str)
    parser.add_argument("--task", type=str)
    parser.add_argument("--output", type=str)

    args = parser.parse_args()
    dataset, task, output = parser.dataset, parser.task, parser.output
    load(dataset, task, output)