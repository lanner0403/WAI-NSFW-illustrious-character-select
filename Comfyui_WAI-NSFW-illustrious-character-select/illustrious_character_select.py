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

character_list_cn = ''
character_dict = {}
action_list = ''
action_dict = {}
wai_llm_config = {}
wai_image_list = []
wai_image_dict = {}

wai_illustrious_character_select_files = [
    {'name': 'wai_action', 'file_path': os.path.join(json_folder, 'wai_action.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/action.json'}, 
    {'name': 'wai_zh_tw', 'file_path': os.path.join(json_folder, 'wai_zh_tw.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/zh_TW.json'},
    {'name': 'wai_settings', 'file_path': os.path.join(json_folder, 'wai_settings.json'), 'url': 'https://raw.githubusercontent.com/lanner0403/WAI-NSFW-illustrious-character-select/refs/heads/main/settings.json'},
    # local cache
    {'name': 'wai_image', 'file_path': os.path.join(json_folder, 'wai_image.json'), 'url': 'local'},
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
    You are a Stable Diffusion prompt writer. Follow these guidelines to generate prompts:
    1.Prohibited keywords: Do not use any gender-related words such as "man," "woman," "boy," "girl," "person," or similar terms.
    2.Format: Provide 8 to 16 keywords separated by commas, keeping the prompt concise.
    3.Content focus: Concentrate solely on visual elements of the image; avoid abstract concepts, art commentary, or descriptions of intent.
    4.Keyword categories: Ensure the prompt includes keywords from the following categories:
        - Theme or style (e.g., cyberpunk, fantasy, wasteland)
        - Location or scene (e.g., back alley, forest, street)
        - Visual elements or atmosphere (e.g., neon lights, fog, ruined)
        - Camera angle or composition (e.g., front view, side view, close-up)
        - Action or expression (e.g., standing, jumping, smirk, calm)
        - Environmental details (e.g., graffiti, trees)
        - Time of day or lighting (e.g., sunny day, night, golden hour)
        - Additional effects (e.g., depth of field, blurry background)
    5.Creativity and coherence: Select keywords that are diverse and creative, forming a vivid and coherent scene.
    6.User input: Incorporate the exact keywords from the user's query into the prompt where appropriate.
    7.Emphasis handling: If the user emphasizes a particular aspect, you may increase the number of keywords in that category (up to 6), but ensure the total number of keywords remains between 8 and 16.
    8.Character description: You may describe actions and expressions but must not mention specific character traits (such as gender or age). Words that imply a character (e.g., "warrior") are allowed as long as they do not violate the prohibited keywords.
    9.Output: Provide the answer as a single line of comma-separated keywords.
    Prompt for the following theme:
    """)

def decode_response(response):
    if response.status_code == 200:
        ret = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f'[{cat}]:Response:{ret}')
        # Renmove <think> for DeepSeek
        if str(ret).__contains__('</think>'):
            ret = str(ret).split('</think>')[-1].strip()
            print(f'\n[{cat}]:Trimed response:{ret}')    
            
        ai_text = ret.strip()
        if ai_text.endswith('.'):
            ai_text = ai_text[:-1] + ','      
        if not ai_text.endswith(','):
            ai_text = f'{ai_text},'            
        return ai_text    
    else:
        print(f"[{cat}]:Error: Request failed with status code {response.status_code}")
        return []

def EncodeImage(src_image):
    img = np.array(src_image).astype(np.float32) / 255.0
    img = torch.from_numpy(img)[None,]
    return img

def decode_response(response):
    if response.status_code == 200:
        ret = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f'[{cat}]:Response:{ret}')
        # Renmove <think> for DeepSeek
        if str(ret).__contains__('</think>'):
            ret = str(ret).split('</think>')[-1].strip()
            print(f'\n[{cat}]:Trimed response:{ret}')    
            
        ai_text = ret.strip()
        if ai_text.endswith('.'):
            ai_text = ai_text[:-1] + ','      
        if not ai_text.endswith(','):
            ai_text = f'{ai_text},'            
        return ai_text    
    else:
        print(f"[{cat}]:Error: Request failed with status code {response.status_code}")
        return []

def llm_send_request(input_prompt, url, model, api_key, system_prompt=prime_directive):
    data = {
            'model': model,
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(url, headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}, json=data, timeout=30)
    return decode_response(response)
    
class llm_prompt_gen:
    '''
    lanner0403_llm_prompt_gen_node
    
    An AI based prpmpte gen node
    
    Optional:
    system_prompt      - System prompt for AI Gen
    
    Input:  
    url                - The url to your Remote AI Gen
    model              - Model select
    prompt             - Contents that you need AI to generate
    random_action_seed - MUST connect to `Seed Generator`
    
    Output:
    ai_prompt          - Prompts generate by AI
    '''
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "system_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
            "required": {
                "url":("STRING", {
                    "multiline": False,
                    "default": wai_llm_config["base_url"]
                }),
                "model":("STRING", {
                    "multiline": False,
                    "default": wai_llm_config["model"]
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
    FUNCTION = "llm_prompt_node_ex"
    CATEGORY = cat
    
    def llm_prompt_node_ex(self, url, model, prompt, random_action_seed, system_prompt=prime_directive):
        _ = random_action_seed
        return (llm_send_request(prompt, url, model, wai_llm_config["api_key"], system_prompt),)   

def llm_send_local_request(input_prompt, server, temperature=0.5, n_predict=512, system_prompt=prime_directive):
    data = {
            "temperature": temperature,
            "n_predict": n_predict,
            "cache_prompt": True,
            "stop": ["<|im_end|>"],
            'messages': [
                {"role": "system", "content": system_prompt},
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

    Optional:
    system_prompt      - System prompt for AI Gen

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
            "optional": {
                "system_prompt": ("STRING", {
                    "display": "input" ,
                    "multiline": True
                }),                      
            },
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
    
    def local_llm_prompt_gen_ex(self, server, temperature, n_predict, prompt, random_action_seed, system_prompt=prime_directive):
        _ = random_action_seed
        return (llm_send_local_request(prompt, server, temperature=temperature, n_predict=n_predict, system_prompt=system_prompt),)     
    
class illustrious_character_select:
    '''
    illustrious_character_select
    
    Inputs:
    character             - Character
    action                - Action
    optimise_tags         - Fix duplicate or error tags in Character
    random_action_seed    - MUST connect to `Seed Generator`
    
    Optional Input:
    custom_prompt         - An optional custom prompt for final output. E.g. AI Generated ptompt`
        
    Outputs:
    prompt                - Final prompt
    info                  - Debug info
    thumb_image           - Thumb image from Json file, you can use it for preview...
    '''         

    def remove_duplicates(self, input_string):
        items = input_string.split(',')    
        unique_items = list(dict.fromkeys(item.strip() for item in items))    
        result = ', '.join(unique_items)
        return result
                   
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
                "character": (character_list_cn, ),
                "action": (action_list, ),
                "optimise_tags": ("BOOLEAN", {"default": True}),
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
    
    def illustrious_character_select_ex(self, character, action, optimise_tags, random_action_seed, custom_prompt = ''):
        chara = ''
        rnd_character = ''
        act = ''
        rnd_action = ''
        
        if 'random' == character:
            index = random_action_seed % len(character_list_cn)
            rnd_character = character_list_cn[index]
            if 'random' == rnd_character:
                rnd_character = character_list_cn[index+2]
            elif 'none' == rnd_character:
                rnd_character = character_list_cn[index+1]
        else:
            rnd_character = character

        chara = character_dict[rnd_character] 
            
        if 'random' == action:
            index = random_action_seed % len(action_list)
            rnd_action = action_list[index]
            act = f'{action_dict[rnd_action]}, '
        elif 'none' == action:
            rnd_action = action
            act = ''
        else:
            rnd_action = action
            act = f'{action_dict[rnd_action]}, '               
                    
        thumb_image = EncodeImage(Image.new('RGB', (128, 128), (128, 128, 128)))        
        if wai_image_dict.keys().__contains__(chara):
            thumb_image = dase64_to_image(wai_image_dict.get(chara))
        
        opt_chara = chara
        if optimise_tags:
            opt_chara = opt_chara.split(',')[1].strip()
            opt_chara = opt_chara.replace('(', '\\(').replace(')', '\\)')
            if not opt_chara.endswith(','):
                opt_chara = f'{opt_chara},'  
            
        prompt = f'{opt_chara}, {act}{custom_prompt}'
        info = f'Character:{rnd_character}[{opt_chara}]\nAction:{rnd_action}[{act}]\nCustom prompt:{custom_prompt}'
                
        return (prompt, info, thumb_image, )
    
class illustrious_character_select_en:
    '''
    Same as lanner0403_illustrious_character_select
    But list in English tags
    '''                

    def remove_duplicates(self, input_string):
        items = input_string.split(',')    
        unique_items = list(dict.fromkeys(item.strip() for item in items))    
        result = ', '.join(unique_items)
        return result
                   
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
                "character": (character_list_en, ),
                "action": (action_list, ),
                "optimise_tags": ("BOOLEAN", {"default": True}),
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
    FUNCTION = "illustrious_character_select_en_ex"
    CATEGORY = cat
    
    def illustrious_character_select_en_ex(self, character, action, optimise_tags, random_action_seed, custom_prompt = ''):
        chara = ''
        rnd_character = ''
        act = ''
        rnd_action = ''
        
        if 'random' == character:
            index = random_action_seed % len(character_list_en)
            rnd_character = character_list_en[index]
            if 'random' == rnd_character:
                rnd_character = character_list_en[index+2]
            elif 'none' == rnd_character:
                rnd_character = character_list_en[index+1]
        else:
            rnd_character = character
            
        chara = rnd_character        
            
        if 'random' == action:
            index = random_action_seed % len(action_list)
            rnd_action = action_list[index]
            act = f'{action_dict[rnd_action]}, '
        elif 'none' == action:
            rnd_action = action
            act = ''
        else:
            rnd_action = action
            act = f'{action_dict[rnd_action]}, '               
                    
        thumb_image = EncodeImage(Image.new('RGB', (128, 128), (128, 128, 128)))        
        if wai_image_dict.keys().__contains__(chara):
            thumb_image = dase64_to_image(wai_image_dict.get(chara))
        
        opt_chara = chara
        if optimise_tags:
            opt_chara = opt_chara.split(',')[1].strip()
            opt_chara = opt_chara.replace('(', '\\(').replace(')', '\\)')
            if not opt_chara.endswith(','):
                opt_chara = f'{opt_chara},'  
            
        prompt = f'{opt_chara}, {act}{custom_prompt}'
        info = f'Character:{rnd_character}[{opt_chara}]\nAction:{rnd_action}[{act}]\nCustom Promot:{custom_prompt}'
                
        return (prompt, info, thumb_image, )    

def download_file(url, file_path):   
    response = requests.get(url)
    response.raise_for_status() 
    print('[{}]:Downloading... {}'.format(cat, url))
    with open(file_path, 'wb') as file:
        file.write(response.content)        

def dase64_to_image(base64_data):
    base64_str = base64_data.split("base64,")[1]
    image_data = base64.b64decode(base64_str)
    image_bytes = BytesIO(image_data)
    image = Image.open(image_bytes)    
    return EncodeImage(image)

def main():
    global character_list_cn
    global character_list_en
    global character_dict
    global action_list
    global action_dict
    global wai_llm_config
    global wai_image_dict
    
    wai_image_cache = False
    wai_image_dict_temp = {}
    
    # download file
    for item in wai_illustrious_character_select_files:
        name = item['name']
        file_path = item['file_path']
        url = item['url']        
            
        if 'local' == url and 'wai_image' == name:
            if os.path.exists(file_path):
                wai_image_cache = True   
            else:
                continue
        else:
            if not os.path.exists(file_path):
                download_file(url, file_path)

        with open(file_path, 'r', encoding='utf-8') as file:
            # print('[{}]:Loading... {}'.format(cat, url))
            if 'wai_action' == name:
                action_dict.update(json.load(file))
                action_list = list(action_dict.keys())
                action_list.insert(0, "none")
            elif 'wai_zh_tw' == name:            
                character_dict.update(json.load(file))
                character_list_cn = list(character_dict.keys())    
                character_list_cn.insert(0, "random")
                
                character_list_en = list(character_dict.values())   
                character_list_en.insert(0, "random")
            elif 'wai_settings' == name:
                wai_llm_config.update(json.load(file))       
            elif 'wai_image' == name and wai_image_cache:
                print('[{}]:Loading wai_image.json, delete this file for update.'.format(cat))
                wai_image_dict = json.load(file)
            elif name.startswith('wai_output_') and not wai_image_cache:
                # [ {} ] .......
                # Got some s..special data format from the source
                # Luckily we have a strong enough cpu for that.
                wai_image_dict_temp = json.load(file)
                for item in wai_image_dict_temp:
                    key = list(item.keys())[0]
                    value = list(item.values())[0]
                    wai_image_dict.update({key : value}) 
        
        if wai_image_cache:
            break
        
    # Create cache
    # Loading time 4.3s to 0.1s
    if not wai_image_cache:
        print('[{}]:Creating wai_image.json ...'.format(cat))
        with open(os.path.join(json_folder, 'wai_image.json'), 'w', encoding='utf-8') as file:
            json.dump(wai_image_dict, file, ensure_ascii=False, indent=4)
            
#if __name__ == '__main__':
main()
