from transformers import BartForConditionalGeneration, BartTokenizer
from transformers import pipeline
import textdistance as td
import obfuscation as obf
import re

def paraphrase_sentence(sentence, num_return_sequences=5):
    """
        
    """
    paraphrase_pipeline = pipeline("text2text-generation", model="eugenesiow/bart-paraphrase")
    results = paraphrase_pipeline(
        sentence,
        num_return_sequences=num_return_sequences,
        num_beams=num_return_sequences,  
        max_length=500
    )
    return [result['generated_text'] for result in results]

def remove_docstrings(code):
    pattern = r'""".*?"""|\'\'\'.*?\'\'\''
    return re.sub(pattern, '', code, flags=re.DOTALL)

def pertubation_nl(input : str, max_pert : int = 5):
    prt = [input]
    prt.extend(paraphrase_sentence(input))
    for p in prt:
        rs.append({'prompt' : p, 'distance' : td.cosine.distance(prt[0], p)})
        rs = sorted(rs, key=lambda x: x['distance'])
    return rs

def perturbation_code(input : str, language : str = 'python', max_pert : int = 5):
    rs, obf = [], obf.CrossLanguageObfuscator()
    noise_max = min(max_pert, obf.len_identifiers(input, language))
    for i in range(noise_max):
        code_alt = obf.level1_rename_variables(input, language, i)
        rs.append({'noise': i, 'prompt' : code_alt, 'distance' : td.cosine.distance(input, code_alt)})         
    return rs

def build_test_prompt(func_name, program, description):
    program = remove_docstrings(program)
    return f'''Please write a test method for the function '{func_name}' given the following program under test and function description. Your answer should only contain one test input.
Program under test:
----
{program}
----
Function description for '{func_name}':
----
{description}
----
Your test method should begin with:
def test_{func_name}():
    solution=Solution()'''

def func_name(program):
    return program.split('def ')[-1].split('(')[0]