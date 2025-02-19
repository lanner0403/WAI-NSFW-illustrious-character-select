import os
import textwrap
import numpy as np
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import torch

# CATEGORY
cat = "Mira/CS"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder = os.path.join(current_dir, "json")

character_list = ''
character_dict = {}
action_list = ''
action_dict = {}
wai_llm_config = {}
wai_image = {}

wai_illustrious_character_select_files = [
    {'name': 'wai_action', 'file_path': os.path.join(json_folder, 'wai_action.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/action.json'}, 
    {'name': 'wai_zh_tw', 'file_path': os.path.join(json_folder, 'wai_zh_tw.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/zh_TW.json'},
    {'name': 'wai_settings', 'file_path': os.path.join(json_folder, 'wai_settings.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/settings.json'},
    # images
    {'name': 'wai_output_1', 'file_path': os.path.join(json_folder, 'wai_output_1.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_1.json'},
    {'name': 'wai_output_2', 'file_path': os.path.join(json_folder, 'wai_output_2.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_2.json'},
    {'name': 'wai_output_3', 'file_path': os.path.join(json_folder, 'wai_output_3.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_3.json'},
    {'name': 'wai_output_4', 'file_path': os.path.join(json_folder, 'wai_output_4.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_4.json'},
    {'name': 'wai_output_5', 'file_path': os.path.join(json_folder, 'wai_output_5.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_5.json'},
    {'name': 'wai_output_6', 'file_path': os.path.join(json_folder, 'wai_output_6.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_6.json'},
    {'name': 'wai_output_7', 'file_path': os.path.join(json_folder, 'wai_output_7.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_7.json'},
    {'name': 'wai_output_8', 'file_path': os.path.join(json_folder, 'wai_output_8.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_8.json'},
    {'name': 'wai_output_9', 'file_path': os.path.join(json_folder, 'wai_output_9.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_9.json'},
    {'name': 'wai_output_10', 'file_path': os.path.join(json_folder, 'wai_output_10.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/output_10.json'},
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
        print(f'{cat}: Response:{ret}')
        # Renmove <think> for DeepSeek
        if str(ret).__contains__('</think>'):
            ret = str(ret).split('</think>')[-1].strip()
            print(f'{cat}: Trimed response:{ret}')        
        return ret
    else:
        print(f"Error: Request failed with status code {response.status_code}")
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
    
class llm_prompt_gen:
    '''
    llm_prompt_gen
    
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

def llm_send_local_request(input_prompt, server, temperature=0.5, n_predict=512):
    data = {
            "temperature": temperature,
            "n_predict": n_predict,
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
    llama-server.exe -ngl 40 --no-mmap -m "F:\\LLM\\Meta-Llama\\GGUF_Versatile-Llama-3-8B.Q8_0\\Versatile-Llama-3-8B.Q8_0.gguf"

    For DeepSeek, you may need a larger n_predict 2048~ and lower temperature 0.4~, for llama3.3 256~512 may enough.

    Input:
    server             - Your llama_cpp server addr. E.g. http://127.0.0.1:8080/chat/completions
    temperature        - A parameter that influences the language model's output, determining whether the output is more random and creative or more predictable.
    n_predict          - Controls the number of tokens the model generates in response to the input prompt
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
                "temperature": ("FLOAT", {
                    "min": 0.1,
                    "max": 1,
                    "step": 0.05,
                    "default": 0.5
                }),
                "n_predict": ("INT", {
                    "min": 128,
                    "max": 4096,
                    "step": 128,
                    "default": 256
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
    
    def local_llm_prompt_gen_ex(self, server, temperature, n_predict, prompt, random_action_seed):
        _ = random_action_seed
        return (llm_send_local_request(prompt, server, temperature=temperature, n_predict=n_predict),)     
    
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
    thumb_image           - Thumb image from Json file, you can use it for preview...
    '''         
    
    def EncodeImage(self, src_image):
        img = np.array(src_image).astype(np.float32) / 255.0
        img = torch.from_numpy(img)[None,]
        return img

    def update_image(self, base64_data):
        #print(base64_data)
        base64_str = base64_data.split("base64,")[1]
        image_data = base64.b64decode(base64_str)
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        return self.EncodeImage(image)
           
    @classmethod
    def INPUT_TYPES(s):
        
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
                        
    RETURN_TYPES = ("STRING","STRING", "IMAGE",)
    RETURN_NAMES = ("prompt", "info", "thumb_image",)    
    FUNCTION = "illustrious_character_select_ex"
    CATEGORY = cat
    OUTPUT_NODE = True
    
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
            act = f'{action_dict[rnd_action]}, '
        elif 'none' == action:
            act = ''
        else:
            act = f'{action_dict[action]}, '
        
        prompt = f'{chara}, {act}{custom_prompt}'
        info = f'Character:{rnd_character}[{chara}]\nAction:{act}\nCustom Promot:{custom_prompt}'
        
        if wai_image.keys().__contains__(chara):
            print(f'{cat}: Found Thumb Image:{chara}')
            thumb_image = self.update_image(wai_image.get(chara))
            results = list()
            results.append({
                "filename": 'tmp.png',
                "subfolder": json_folder,
                "type": 'output'
            })
            return (prompt, info, thumb_image,)
        
        return (prompt, info, None,)

def download_file(url, file_path):
    response = requests.get(url)
    response.raise_for_status() 
    print('{}:Downloading... {}'.format(cat, url))
    with open(file_path, 'wb') as file:
        file.write(response.content)

def main():
    global character_list
    global character_dict
    global action_list
    global action_dict
    global wai_llm_config
    global wai_image
    
    wai_image_temp = {}
    # download file
    for item in wai_illustrious_character_select_files:
        name = item['name']
        file_path = item['file_path']
        url = item['url']
        
        if not os.path.exists(file_path):
            download_file(url, file_path)

        with open(file_path, 'r', encoding='utf-8') as file:
            # print('{}:Loading... {}'.format(cat, url))
            if 'wai_action' == name:
                action_dict.update(json.load(file))
            elif 'wai_zh_tw' == name:            
                character_dict.update(json.load(file))
            elif 'wai_settings' == name:
                wai_llm_config.update(json.load(file))       
            elif name.startswith('wai_output_'):
                # [ {} ] .......
                # Got some s..special data format from the source
                # Luckily we have a strong enough cpu for that.
                # Maybe, we could rewrite the data format in the future.
                wai_image_temp = json.load(file)
                
                for item in wai_image_temp:
                    key = list(item.keys())[0]
                    value = list(item.values())[0]
                    wai_image.update({key : value})                     
            
    action_list = list(action_dict.keys())
    action_list.insert(0, "none")
    character_list = list(character_dict.keys())    
    character_list.insert(0, "random")

#if __name__ == '__main__':
main()
