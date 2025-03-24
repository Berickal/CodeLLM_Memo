import ollama, tqdm, pandas, os, json, re, time, argparse
from utils import get_data, clean_code

def get_instruction(key):
    if key == "cg" :
        return "Provide as output a python code related to this task."
    elif key == "tg" :
        return ""
    elif key == "pr" :
        return "Provide a fix for the buggy function."
    elif key == "vd" :
        return "Examine the following code for security flaw and provide as output a summary of the vulnerability containing in 100 words max."
    elif key == "cs" :
        return "Examine the following code and provide as output a summary of this code in 100 words max."
    else:
        return None

def generate(model : str, folder : str, output : str, task : str = 'cg', max_iter = 3):
    """
        cg -> Code Generation | tg -> Test Generation | pr -> Program Repair | vd -> Vulnerability Detection | cs -> Code Summarization
    """
    instruct = get_instruction(task)
    files = [pos_json for pos_json in os.listdir(folder) if pos_json.endswith('.json')]
    for idx, file in tqdm(enumerate(files), total=len(files)):
        data = get_data(folder + file)
        for p in data['pert']:
            rs = []
            for _ in range(max_iter):
                prt = [{"role" : "system", "content" : instruct}, 
                       {"role" : "user", "content" : prt["prompt"]}]
                rs.append(ollama.chat(model=model, prompt=prt))
            p['gen'] = rs
        with open(f'{output}{file}', 'w') as nf:
            json.dump(data, nf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    parser.add_argument("--folder", type=str)
    parser.add_argument("--task", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--iteration", type=int, default=3)

    args = parser.parse_args()

    fol, task, out, iter, model = args.folder, args.task, args.output, args.iteration, args.model
    generate(model, fol, out, task, iter)
    