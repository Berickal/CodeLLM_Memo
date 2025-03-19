from tree_sitter import Language, Parser
import random
import string
from typing import List, Dict
import ast, tiktoken
import re
from tree_sitter_languages import get_language, get_parser

class CrossLanguageObfuscator:
    def __init__(self):        
        self.languages = {
            'python': get_language('python'),
            'java': get_language('java'),
            'javascript': get_language('javascript'),
            'c': get_language('c')
        }
        
        self.parser = Parser()
        self.name_mapping = {}
        
        # Languages Keywords
        self.preserved_keywords = {
            'python': {'def', 'return', 'class', 'if', 'else', 'while', 'for', 'in', 'print', 'int', 'List', 'list', 'tuple', 'Tuple', 'Float', 'float', 'ndarray', 'array'},
            'java': {'public', 'private', 'class', 'static', 'void', 'String', 'System', 'out'},
            'c' : {'int', 'char', 'void', 'return', 'if', 'else', 'while', 'for', 'struct', 'typedef', 'printf', 'scanf', 'malloc', 'free'},
            'javascript' : {'let', 'try', 'func', 'export', 'finally', 'double', 'char', 'abstract', 'const', 'for', 'while', 'else', 'return'}
        }
    
    def generate_random_name(self, length: int = 8) -> str:
        """Generate random variable/function names."""
        return '_' + ''.join(random.choices(string.ascii_letters, k=length))
    
    def len_identifiers(self, code: str, language: str) -> int:
        self.parser.set_language(self.languages[language])
        tree, id = self.parser.parse(bytes(code, 'utf8')), []
        cursor = tree.walk()
        for node in self._traverse_tree(cursor):
            if node.type in ['identifier'] :
                name = code[node.start_byte:node.end_byte]
                if name not in self.preserved_keywords[language] and not name.startswith('__') and not name.isupper():
                    id.append(name)
        return len(set(id))
    
    def add_importlib(self, code: str, language: str):
        lines = code.splitlines()
        for l in lines:
            if 'import ' in l:
                self.preserved_keywords['python'].update(set(l.replace(',', '').split()))
    
    def level1_rename_variables(self, code: str, language: str, lim: int = 1000) -> str:
        """ Obfuscation level 1: Variable and function renaming, excluding class and function names """

        self.parser.set_language(self.languages[language])
        modified_code, tree = code, self.parser.parse(bytes(code, 'utf8'))
        self.name_mapping = {}
        self.add_importlib(code, language)

        def should_rename(node):
            name = code[node.start_byte:node.end_byte]
            parent = node.parent
            if parent and parent.type in ["class_definition", "function_definition", "class_declaration", "method_declaration"]:
                return False
            
            if parent and parent.type == "method_invocation":
                first_child = parent.child_by_field_name("object") 
                if first_child and first_child == node:
                    return True
                return False

            return (name not in self.preserved_keywords[language] and 
                    not name.startswith('__') and not name.isupper())

        # Collect identifiers and map each one with a generated value
        cursor = tree.walk()
        for node in self._traverse_tree(cursor):
            if node.type == 'identifier' and should_rename(node):
                original_name = code[node.start_byte:node.end_byte]
                if isinstance(original_name, bytes):
                    original_name = original_name.decode('utf-8')
                if original_name not in self.name_mapping and len(self.name_mapping) < lim:
                    self.name_mapping[original_name] = self.generate_random_name()

        # Replace identifiers
        replacements = []
        cursor = tree.walk()
        for node in self._traverse_tree(cursor):
            if node.type == 'identifier' and should_rename(node):
                original_name = code[node.start_byte:node.end_byte]
                if isinstance(original_name, bytes):
                    original_name = original_name.decode('utf-8')
                if original_name in self.name_mapping:
                    replacements.append((node.start_byte, node.end_byte, self.name_mapping[original_name]))

        # Apply replacements in reverse order to maintain correct positions
        for start, end, new_name in sorted(replacements, reverse=True):
            modified_code = modified_code[:start] + new_name + modified_code[end:]

        return modified_code

    
    def level2_add_dead_code(self, code: str, language: str) -> str:
        """ Obfuscation level 2: Add dead code and dummy functions
        """
        dead_code_templates = {
            'python': [
                '\n    if False:\n        print("Unreachable")\n',
                '\n    while False:\n        pass\n',
                '\n    def {}():\n        return None\n'.format(self.generate_random_name())
            ],
            'java': [
                '\n    if (false) { System.out.println("Unreachable"); }\n',
                '\n    while (false) { break; }\n',
                '\n    private void {}() {{ return; }}\n'.format(self.generate_random_name())
            ],
            'c': [
                '\nif (0) { printf("Unreachable\\n"); }\n',
                '\nwhile (0) { break; }\n',
                f'\nvoid {self.generate_random_name()}() {{ return; }}\n',
                f'\n#define {self.generate_random_name()}(x) (x)\n'
            ]
        }
        
        # Insert random dead code blocks
        modified_code = code
        templates = dead_code_templates[language]
        
        # Find appropriate insertion points
        if language == 'python':
            # Insert at function level
            lines = modified_code.split('\n')
            for i in range(len(lines)):
                if lines[i].strip().startswith('def '):
                    lines.insert(i + 1, random.choice(templates))
            modified_code = '\n'.join(lines)
        else:  # Java
            # Insert inside class body
            class_end = modified_code.rfind('}')
            if class_end != -1:
                for _ in range(2):
                    modified_code = (
                        modified_code[:class_end] +
                        random.choice(templates) +
                        modified_code[class_end:]
                    )
        
        return modified_code

    def _traverse_tree(self, cursor):
        """Helper method to traverse Tree-sitter AST."""
        reached_root = False
        while not reached_root:
            yield cursor.node
            
            if cursor.goto_first_child():
                continue
                
            if cursor.goto_next_sibling():
                continue
                
            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True
                elif cursor.goto_next_sibling():
                    retracing = False
    
    def level3_control_flow_obfuscation(self, code: str, language: str) -> str:
        """
        Level 3: Control flow obfuscation
        Transforms control structures to make code harder to follow
        """
        self.parser.set_language(self.languages[language])
        tree = self.parser.parse(bytes(code, 'utf8'))
        
        control_flow_templates = {
            'python': {
                'if': {
                    'pattern': r'if (.*?):',
                    'replacement': 'if True:\n    if not ({}):\n        pass\n    else:'
                },
                'while': {
                    'pattern': r'while (.*?):',
                    'replacement': 'while True:\n    if not ({}):\n        break'
                }
            },
            'java': {
                'if': {
                    'pattern': r'if \((.*?)\)',
                    'replacement': 'if (true && ({}))'
                },
                'while': {
                    'pattern': r'while \((.*?)\)',
                    # Using string concatenation instead of format to handle curly braces
                    'replacement': 'while (true) {\n    if (!({0})) break;\n'
                }
            },
            'c' : {
                'if': {
                    'pattern': r'if \((.*?)\)',
                    'replacement': 'if (1 && ({}))'
                },
                'while': {
                    'pattern': r'while \((.*?)\)',
                    'replacement': 'while (1) { if (!({0})) break;'
                },
                'for': {
                    'pattern': r'for \((.*?;.*?;.*?)\)',
                    'replacement': 'for ({0}) {{ if (!(1)) break;'
                }
            }
        }
        
        modified_code = code
        import re
        
        # Transform control structures
        templates = control_flow_templates[language]
        for struct_type, template in templates.items():
            matches = re.finditer(template['pattern'], modified_code)
            # Process matches in reverse to maintain string indices
            matches = list(matches)
            for match in reversed(matches):
                condition = match.group(1)
                # Handle Java curly braces specially
                if language == 'java' and struct_type == 'while':
                    new_structure = (
                        'while (true) {\n'
                        f'    if (!({condition})) break;\n'
                    )
                else:
                    new_structure = template['replacement'].format(condition)
                
                modified_code = (
                    modified_code[:match.start()] +
                    new_structure +
                    modified_code[match.end():]
                )
        
        return modified_code
    
    def level4_string_encryption(self, code: str, language: str) -> str:
        """
        Level 4: String encryption
        Encrypts string literals and adds decryption routine
        """
        self.parser.set_language(self.languages[language])
        tree = self.parser.parse(bytes(code, 'utf8'))
        
        # Define decryption functions for each language
        decrypt_functions = {
            'python': '''
def _decrypt(s: str, key: int = 13) -> str:
    return ''.join(chr(ord(c) ^ key) for c in s)
    ''',
            'java': '''
        private static String _decrypt(String s, int key) {
            StringBuilder result = new StringBuilder();
            for (char c : s.toCharArray()) {
                result.append((char)(c ^ key));
            }
            return result.toString();
        }
    ''',
            'c': '''
char* _decrypt(const char* s, int key) {
    int len = strlen(s);
    char* result = (char*)malloc(len + 1);
    for(int i = 0; i < len; i++) {
        result[i] = s[i] ^ key;
    }
    result[len] = '\\0';
    return result;
}
'''
        }
        
        # Simple XOR encryption
        def encrypt_string(s: str, key: int = 13) -> str:
            return ''.join(chr(ord(c) ^ key) for c in s)
        
        modified_code = code
        
        # Add decryption function
        if language == 'python':
            modified_code = decrypt_functions[language] + modified_code
        elif language == 'java':
            # Insert before the last class closing brace
            last_brace = modified_code.rindex('}')
            modified_code = (
                modified_code[:last_brace] +
                decrypt_functions[language] +
                modified_code[last_brace:]
            )
        
        # Find and encrypt string literals
        cursor = tree.walk()
        replacements = []
        
        for node in self._traverse_tree(cursor):
            if node.type == 'string' or node.type == 'string_literal':
                # Extract the string content
                string_content = code[node.start_byte:node.end_byte]
                if isinstance(string_content, bytes):
                    string_content = string_content
                
                # Remove quotes
                if string_content.startswith(('"""', "'''", '"', "'")):
                    quote_char = string_content[0]
                    string_content = string_content.strip(quote_char)
                    
                    # Encrypt the string
                    encrypted = encrypt_string(string_content)
                    
                    # Create decryption call
                    if language == 'python':
                        replacement = f'_decrypt("{encrypted}")'
                    else:  # java
                        replacement = f'_decrypt("{encrypted}", 13)'
                    
                    replacements.append((node.start_byte, node.end_byte, replacement))
        
        # Apply replacements in reverse order
        for start, end, replacement in sorted(replacements, reverse=True):
            modified_code = (
                modified_code[:start] +
                replacement +
                modified_code[end:]
            )
        
        return modified_code
    
    # Add to the obfuscate method:
    def obfuscate(self, code: str, language: str, level: int = 1) -> str:
        """
        Main obfuscation method. Applies obfuscation techniques up to specified level.
        """
        modified_code = code
        
        if level >= 1:
            modified_code = self.level1_rename_variables(modified_code, language)
        if level >= 2:
            modified_code = self.level2_add_dead_code(modified_code, language)
        if level >= 3:
            modified_code = self.level3_control_flow_obfuscation(modified_code, language)
        if level >= 4:
            modified_code = self.level4_string_encryption(modified_code, language)
            
        return modified_code
    

class BitFlip:
    def __init__(self, input):
        self.input = input
        self.enc = tiktoken.encoding_for_model("gpt-4o")
        self.tokens = self.enc.encode(input)
        self.bin = []
        for tok in self.tokens:
            self.bin.append(format(tok, 'b'))

    def bit_flip(self, bit):
        return 0 if bit == '1' else 1

    def flip(self, prob : list[int]):
        bin_flip = []
        for tok in self.bin:
            n_tok = -1
            while (n_tok > self.enc.max_token_value) or (n_tok < 0):
                rd_ = random.choices([0, 1], weights = prob, k = len(tok))
                fl = ''
                for idx, b in enumerate(rd_):
                    fl += str(tok[idx]) if b == 0 else str(self.bit_flip(tok[idx]))
                n_tok = int(fl, 2)
            bin_flip.append(n_tok)
        return bin_flip, self.enc.decode(bin_flip)