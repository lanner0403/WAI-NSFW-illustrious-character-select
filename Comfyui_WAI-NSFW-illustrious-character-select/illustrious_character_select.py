import os
import textwrap
import requests
import json

# CATEGORY
cat = "Mira/CS"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder = os.path.join(current_dir, "json")

character_list = ''
character_dict = {}
action_list = ''
action_dict = {}
wai_llm_config = {}

wai_illustrious_character_select_files = [
    # images
    # {'name': 'wai_json_file1', 'file_path': os.path.join(json_folder, 'wai_mq7yf9.json'), 'url': 'https://files.catbox.moe/mq7yf9.json'}, 
    # {'name': 'wai_json_file2', 'file_path': os.path.join(json_folder, 'wai_6holoy.json'), 'url': 'https://files.catbox.moe/6holoy.json'},  
    {'name': 'wai_action', 'file_path': os.path.join(json_folder, 'wai_action.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/action.json'}, 
    {'name': 'wai_zh_tw', 'file_path': os.path.join(json_folder, 'wai_zh_tw.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/zh_TW.json'},
    {'name': 'wai_settings', 'file_path': os.path.join(json_folder, 'wai_settings.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/settings.json'},    
]

prime_directive = textwrap.dedent("""\
    Act as a prompt maker with the following guidelines:               
    - Break keywords by commas.
    - Provide high-quality, non-verbose, coherent, brief, concise, and not superfluous prompts.
    - Focus solely on the visual elements of the picture; avoid art commentaries or intentions.
    - Construct the prompt with the component format:
    1. Start with the subject and keyword description.
    2. Follow with motion keyword description.
    3. Follow with scene keyword description.
    4. Finish with background and keyword description.
    - Limit yourself to no more than 20 keywords per component  
    - Include all the keywords from the user's request verbatim as the main subject of the response.
    - Be varied and creative.
    - Always reply on the same line and no more than 100 words long. 
    - Do not enumerate or enunciate components.
    - Create creative additional information in the response.    
    - Response in English.
    - Response prompt only.                                                
    The followin is an illustartive example for you to see how to construct a prompt your prompts should follow this format but always coherent to the subject worldbuilding or setting and cosider the elemnts relationship.
    Example:
    Demon Hunter,Cyber City,A Demon Hunter,standing,lone figure,glow eyes,deep purple light,cybernetic exoskeleton,sleek,metallic,glowing blue accents,energy weapons,Fighting Demon,grotesque creature,twisted metal,glowing red eyes,sharp claws,towering structures,shrouded haze,shimmering energy,                            
    Make a prompt for the following Subject:
    """)

def decode_response(response):
    if response.status_code == 200:
        ret = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f'{cat}Response:{ret}')
        return ret
    else:
        print(f"{cat}:Error: Request failed with status code {response.status_code}")
        return []

def llm_send_request(input_prompt, llm_config):
    data = {
            'model': llm_config["model"],
            'messages': [
                {"role": "system", "content": prime_directive},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(llm_config["base_url"], headers={"Content-Type": "application/json", "Authorization": "Bearer " + llm_config["api_key"]}, json=data)
    return decode_response(response)
    
class llm_prompt_node:
    '''
    llm_prompt_node
    
    An AI based prpmpte gen node
    
    Input:
    prompt             - Contents that you need AI to generate
    random_action_seed - MUST connect to `Seed Generator`
    
    Output:
    ai_prompt          - Prompts generate by AI
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),     
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ai_prompt",)
    FUNCTION = "llm_prompt_node_ex"
    CATEGORY = cat
    
    def llm_prompt_node_ex(self, prompt, random_action_seed):
        _ = random_action_seed
        return (llm_send_request(prompt, wai_llm_config),)   

def llm_send_local_request(input_prompt, server):
    data = {
            "temperature": 0.6,
            "n_predict": 128,
            "cache_prompt": True,
            "stop": ["<|im_end|>"],
            'messages': [
                {"role": "system", "content": prime_directive},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(server, headers={"Content-Type": "application/json"}, json=data)

    return decode_response(response)

class mira_local_llm_prompt_gen:
    '''
    local_llm_prompt_gen
    
    An AI based prpmpte gen node for local LLM
    
    Server args:
    llama-server.exe -ngl 40 --no-mmap -m "F:\LLM\Meta-Llama\GGUF_Versatile-Llama-3-8B.Q8_0\Versatile-Llama-3-8B.Q8_0.gguf"
    
    Input:
    server             - Your llama_cpp server addr. E.g. http://127.0.0.1:8080/chat/completions
    prompt             - Contents that you need AI to generate
    random_action_seed - MUST connect to `Seed Generator`
    
    Output:
    ai_prompt          - Prompts generate by AI
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "server": ("STRING", {
                    "default": "http://127.0.0.1:8080/chat/completions", 
                    "display": "input" ,
                    "multiline": False
                }),
                "prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),     
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ai_prompt",)
    FUNCTION = "local_llm_prompt_gen_ex"
    CATEGORY = cat
    
    def local_llm_prompt_gen_ex(self, server, prompt, random_action_seed):
        _ = random_action_seed
        return (llm_send_local_request(prompt, server),)   
    
class illustrious_character_select:
    '''
    illustrious_character_select
    
    Inputs:
    character             - Character
    action                - Action
    random_action_seed    - MUST connect to `Seed Generator`
    
    Optional Input:
    custom_prompt         - An optional custom prompt for final output. E.g. AI Generated ptompt`
        
    Outputs:
    prompt                - Final prompt
    info                  - Debug info
    '''                
    @classmethod
    def INPUT_TYPES(s):
        global action_list
        global character_list
        
        return {
            "optional": {
                "custom_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),      
            },
            "required": {
                "character": (character_list, ),
                "action": (action_list, ),
                "random_action_seed": ("INT", {
                    "default": 1024, 
                    "min": 0, 
                    "max": 0xffffffffffffffff,
                    "display": "input"
                }),
            },
        }
                
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("prompt", "info")
    FUNCTION = "illustrious_character_select_ex"
    CATEGORY = cat
    
    def illustrious_character_select_ex(self, character, action, random_action_seed, custom_prompt = ''):
        chara = ''
        rnd_character = ''
        act = ''
        
        if 'random' == character:
            index = random_action_seed % len(character_list)
            rnd_character = character_list[index]
        else:
            rnd_character = character
        chara = character_dict[rnd_character]
            
        if 'random' == action:
            index = random_action_seed % len(action_list)
            rnd_action = action_list[index]
            act += ", " + action_dict[rnd_action]
        elif 'none' == action:
            act = ''
        else:
            act += ", " + action_dict[action]
        
        prompt = f'{chara}, {act}, {custom_prompt}'
        info = f'Character:{rnd_character}[{chara}]\nAction:{act}\nCustom Promot:{custom_prompt}'
        return (prompt, info,)

def download_file(url, file_path):
    response = requests.get(url)
    response.raise_for_status() 
    with open(file_path, 'wb') as file:
        file.write(response.content)

# download file
for item in wai_illustrious_character_select_files:
    name = item['name']
    file_path = item['file_path']
    url = item['url']
    
    if not os.path.exists(file_path):
        print('{}:Downloading... {}'.format(cat, url))
        download_file(url, file_path)
        
    with open(file_path, 'r', encoding='utf-8') as file:
        print('{}:Loading... {}'.format(cat, url))
        if 'wai_action' == name:
            action_dict.update(json.load(file))
        if 'wai_zh_tw' == name:            
            character_dict.update(json.load(file))
        if 'wai_settings' == name:
            wai_llm_config.update(json.load(file))
    
action_list = list(action_dict.keys())
action_list.insert(0, "none")
character_list = list(character_dict.keys())    
character_list.insert(0, "random")
