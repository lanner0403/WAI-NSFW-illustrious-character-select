import os
import textwrap
import numpy as np
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import random
import gradio as gr
from comfyui import run_comfyui
from webui import run_webui

# CATEGORY
cat = "WAI_Character_Select"

current_dir = os.path.dirname(os.path.abspath(__file__))
json_folder = os.path.join(current_dir, 'json')

character_list = ''
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
        print(f'[{cat}]:Response:{ret}')
        # Renmove <think> for DeepSeek
        if str(ret).__contains__('</think>'):
            ret = str(ret).split('</think>')[-1].strip()
            print(f'[{cat}]:Trimed response:{ret}')        
        return ret
    else:
        print(f"[{cat}]:Error: Request failed with status code {response.status_code}")
        return []


def llm_send_request(input_prompt, llm_config):
    data = {
            'model': llm_config["model"],
            'messages': [
                {"role": "system", "content": prime_directive},
                {"role": "user", "content": input_prompt + ";Response in English"}
            ],  
        }
    response = requests.post(llm_config["base_url"], headers={"Content-Type": "application/json", "Authorization": "Bearer " + llm_config["api_key"]}, json=data, timeout=30)
    return decode_response(response)

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
    return image

def download_jsons():
    global character_list
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
                character_list = list(character_dict.keys())    
                character_list.insert(0, "random")
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
            
            
def remove_duplicates(input_string):
    items = input_string.split(',')    
    unique_items = list(dict.fromkeys(item.strip() for item in items))    
    result = ', '.join(unique_items)
    return result


def illustrious_character_select_ex(character = 'random', action = 'none', optimise_tags = True, random_action_seed = 1, custom_prompt = ''):
    chara = ''
    rnd_character = ''
    act = ''
    rnd_action = ''
    
    if 'random' == character:
        index = random_action_seed % len(character_list)
        rnd_character = character_list[index]
        if 'random' == rnd_character:
            rnd_character = character_list[index+1]
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
                
    thumb_image = Image.new('RGB', (128, 128), (128, 128, 128))
    if wai_image_dict.keys().__contains__(chara):
        thumb_image = dase64_to_image(wai_image_dict.get(chara))
    
    opt_chara = chara
    if optimise_tags:
        opt_chara = remove_duplicates(chara.replace('_', ' ').replace(':', ' '))
        opt_chara = opt_chara.replace('(', '\\(').replace(')', '\\)')
        
    prompt = f'{opt_chara}{act}{custom_prompt},'
    info = f'Character:{rnd_character}[{opt_chara}]\nAction:{rnd_action}[{act}]\nCustom Promot:[{custom_prompt}]'
            
    print(f'\n{prompt}\n')
    print(f'Info:{info}')
    return prompt, info, thumb_image

def parse_api_image_data(api_image_data):
    try:
        cfg, steps, width, height = map(float, api_image_data.split(','))
        return float(cfg), int(steps), int(width), int(height)
    except ValueError:
        return 7.0, 30, 1024, 1360
    
def stream_chat(character='random', action='none', random_seed=-1, custom_prompt='', 
                ai_interface='none', ai_prompt='make character furry', ai_local_addr='http://127.0.0.1:8080/chat/completions', ai_local_temp=0.3, ai_local_n_predict=1536, 
                api_interface='none', api_addr='127.0.0.1:7890', api_prompt='', api_neg_prompt='', api_image_data='7.0,36,1024,1360'
            ) -> tuple[str, str, Image.Image, Image.Image]:
    seed = random_seed
    if random_seed == -1:
        seed = random.randint(0, 4294967295)            
    
    ai_text = ''
    if 'Remote' == ai_interface:
        ai_text = llm_send_request(ai_prompt, wai_llm_config)
    elif 'Local' == ai_interface:
        ai_text = llm_send_local_request(ai_prompt, ai_local_addr, ai_local_temp, ai_local_n_predict)

    if ai_text.__contains__('.'):
        ai_text = ai_text.replace('.','')
        
    prompt, info, thumb_image = illustrious_character_select_ex(character = character, action = action, random_action_seed=seed, custom_prompt=custom_prompt)    
    final_prompt = f'{prompt},\n{ai_text},\n{api_prompt}'
    final_info = f'{info}\nAI Prompt:[{ai_text}]'
    
    api_image = Image.new('RGB', (128, 128), (39, 39, 42))    
    cfg, steps, width, height = parse_api_image_data(api_image_data)
    if 'ComfyUI' == api_interface:        
        image_data_list = run_comfyui(server_address=api_addr, positive_prompt=final_prompt, negative_prompt=api_neg_prompt, random_seed=seed, cfg=cfg, steps=steps, width=width, height=height)
        image_data_bytes = bytes(image_data_list)  
        api_image = Image.open(BytesIO(image_data_bytes))    
    elif 'WebUI' == api_interface:
        api_image = run_webui(server_address=api_addr, positive_prompt=final_prompt, negative_prompt=api_neg_prompt, random_seed=seed, cfg=cfg, steps=steps, width=width, height=height)  
            
    return final_prompt, final_info, thumb_image, api_image
        
if __name__ == '__main__':
    download_jsons()
    
    print(f'[{cat}]:Starting...')
    
    with gr.Blocks() as ui:
        with gr.Row():
            with gr.Column():               
                character = gr.Dropdown(
                    choices=character_list,
                    label="Character list",
                    value="random",
                    allow_custom_value = False,
                )

                action = gr.Dropdown(
                    choices=action_list,
                    label="Action list",
                    value="none",
                    allow_custom_value = False,    
                )
    
                random_seed = gr.Slider(minimum=-1,
                    maximum=4294967295,
                    step=1,
                    value=-1,
                    label="Seed",
                )
                custom_prompt = gr.Textbox(value='', label="Custom Prompt")                
                run_button = gr.Button("Create Prompt")

                # AI Prompt Generator
                ai_interface = gr.Dropdown(
                    choices=['none', 'Remote', 'Local'],
                    label="AI Prompt Generator",
                    value="none",
                    allow_custom_value = False,
                )
                ai_prompt = gr.Textbox(label="AI Prompt")
                ai_local_addr = gr.Textbox(value='http://127.0.0.1:8080/chat/completions', label="Local Llama.cpp server")   
                ai_local_temp = gr.Slider(minimum=0.1,
                    maximum=1,
                    step=0.05,
                    value=0.3,
                    label="Local AI Temperature",
                )
                ai_local_n_predict = gr.Slider(minimum=128,
                    maximum=4096,
                    step=128,
                    value=1536,
                    label="Local AI n_predict",
                )             

                gr.HTML('')
                # API Image Generator
                api_interface = gr.Dropdown(
                    choices=['none', 'ComfyUI', 'WebUI'],
                    label="Local Image Generator API",
                    value="none",
                    allow_custom_value = False,
                )
                api_addr = gr.Textbox(value='127.0.0.1:7860', label="Local Image Generator IP Address:Port")
                api_prompt = gr.Textbox(value='masterpiece, best quality, amazing quality', label="Positive Prompt")   
                api_neg_prompt = gr.Textbox(value='bad quality,worst quality,worst detail,sketch,censor,3d', label="Negative Prompt")                   
                api_image_data = gr.Textbox(value='7.0,30,1024,1360', label="CFG,Step,Width,Height")   
                
            with gr.Column():
                api_image = gr.Image(type="pil", label="Local Image Generator")               
                output_prompt = gr.Textbox(label="Prompt")
                output_info = gr.Textbox(label="Information")
                thumb_image = gr.Image(type="pil", label="Thumb Image")                
        
        run_button.click(fn=stream_chat, 
                         inputs=[character, action, random_seed, custom_prompt, 
                                 ai_interface, ai_prompt, ai_local_addr, ai_local_temp, ai_local_n_predict, 
                                 api_interface, api_addr, api_prompt, api_neg_prompt, api_image_data
                                 ], 
                         outputs=[output_prompt, output_info, thumb_image, api_image])
        
    ui.launch()