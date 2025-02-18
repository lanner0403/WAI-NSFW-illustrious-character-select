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

# NOT a good idea to put API key in node ....
def llm_send_request(input_prompt, llm_config):
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
    data = {
            'model': llm_config["model"],
            'messages': [
                {"role": "system", "content": prime_directive},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(llm_config["base_url"], headers={"Content-Type": "application/json", "Authorization": "Bearer " + llm_config["api_key"]}, json=data)

    if response.status_code == 200:
        ret = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f'{cat}Response:{ret}')
        return ret
    else:
        print(f"{cat}:Error: Request failed with status code {response.status_code}")
        return []
    
class llm_prompt_node:
    '''
    llm_prompt_node
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),     
            }
        }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "llm_prompt_node_ex"
    CATEGORY = cat
    
    def llm_prompt_node_ex(self, prompt):
        return (llm_send_request(prompt, wai_llm_config),)
    
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
