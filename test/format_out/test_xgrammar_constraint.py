import time
import requests
import json
import threading
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("/mnt/nvme0/models/Meta-Llama-3.1-8B-Instruct")


class RequestThread(threading.Thread):
    def __init__(self, url, headers, data):
        threading.Thread.__init__(self)
        self.url = url
        self.headers = headers
        self.data = data

    def run(self):
        response = requests.post(self.url, headers=self.headers, data=json.dumps(self.data))
        if response.status_code == 200:
            print(response.json())
        else:
            print("Error:", response.status_code, response.text)


url = "http://0.0.0.0:8888/generate"
headers = {"Content-Type": "application/json"}
json_grammar_ebnf_str = r"""
root ::= basic_array | basic_object
basic_any ::= basic_number | basic_string | basic_boolean | basic_null | basic_array | basic_object
basic_integer ::= ("0" | "-"? [1-9] [0-9]*) ".0"?
basic_number ::= ("0" | "-"? [1-9] [0-9]*) ("." [0-9]+)? ([eE] [+-]? [0-9]+)?
basic_string ::= (([\"] basic_string_1 [\"]))
basic_string_1 ::= "" | [^"\\\x00-\x1F] basic_string_1 | "\\" escape basic_string_1
escape ::= ["\\/bfnrt] | "u" [A-Fa-f0-9] [A-Fa-f0-9] [A-Fa-f0-9] [A-Fa-f0-9]
basic_boolean ::= "true" | "false"
basic_null ::= "null"
basic_array ::= "[" ("" | ws basic_any (ws "," ws basic_any)*) ws "]"
basic_object ::= "{" ("" | ws basic_string ws ":" ws basic_any ( ws "," ws basic_string ws ":" ws basic_any)*) ws "}"
ws ::= [ \n\t]*
"""

json_schema_str = r"""
{
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "金额": {
                "type": "number"
            },
            "标题": {
                "type": "string"
            },
            "类型": {
                "type": "string"
            },
            "大类": {
                "type": "string"
            },
            "小类": {
                "type": "string"
            },
            "日期": {
                "type": "string"
            },
            "时间": {
                "type": "string"
            }
        },
        "required": [
            "金额",
            "标题",
            "类型",
            "大类",
            "小类",
            "时间"
        ]
    }
}
"""

person_schema = r"""{
  "title": "Person",
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "age": {
      "type": "integer",
    }
  },
  "required": ["name", "age"]
}
"""

system_prompt = open("system.md", "r").read()
user_input = open("user.md", "r").read()

# user_input = """generate a person information for me, for example, {'name': 'John', 'age': 25}."""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

inputs = tokenizer.apply_chat_template(messages, tokenize=False)

for i in range(1):
    data = {
        "inputs": inputs,
        # 'temperature': 0.1,
        "parameters": {
            "do_sample": False,
            # "guided_json": json_schema_str,
            "max_new_tokens": 200,
        },
    }
    thread = RequestThread(url, headers, data)
    thread.start()

# time.sleep(2)

# for i in range(20):
#     data = {
#         "inputs": "12-(25+16)*7=",
#         "parameters": {
#             "do_sample": False,
#             "ignore_eos": True,
#             "max_new_tokens": 200,
#             "guided_grammar": r"""root ::= (expr "=" term)+
# expr  ::= term ([-+*/] term)*
# term  ::= num | "(" expr ")"
# num   ::= [0-9]+""",
#         },
#     }
#     thread = RequestThread(url, headers, data)
#     thread.start()
