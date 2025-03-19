import json

def get_data(file : str):
    with open(file, 'r') as j:
         data = json.loads(j.read())
    return data

def clean_code(code):
    """ 
        Clean the answers
    """
    for delim in ['```python', '```C++', '```cpp', '```java', '```javascript', '```c', '```php', '```']:
        if delim in code :
            code = code.split(delim)[1].split('```')[0]
    return code
