import json
from urllib import request, parse
import os
from typing import Dict, Any, Optional
import time
import random
import sys
import uuid
import websocket
import re

ws = None

TRIGGER_LEFT = "CSTART "
TRIGGER_RIGHT = "CEND"

class ComfyUIAPIGenerator:
    def __init__(self, server_address: str = "127.0.0.1:8188", client_id = "4d42d601-ffd1-4573-9311-38d3ea2faa1c", workflow_path: Optional[str] = None):        
        self.server_address = server_address    
        self.client_id = client_id
        if workflow_path is None:
            self.workflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflow.json')
        else:
            self.workflow_path = workflow_path
        
        self.nodes = self.load_workflow()

    def load_workflow(self) -> Dict[str, Any]:
        try:
            with open(self.workflow_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in workflow file: {self.workflow_path}")
    
    def set_png_filename(self, filename: str, node_id: str) -> None:       
        str_prompt = '%time_%seed' + '_' + filename.replace(' ', '_').replace('\\', '').replace(':0.7', '').replace(',', '_') 
        self.nodes[node_id]["inputs"]["filename"] = str_prompt

    def reset_postive_prompt(self,node_id: str) -> None:
        self.nodes[node_id]["inputs"]["text"] = "_____QUALITY_____, _____ARTIST_____, _____PLACE_____, _____POSE_____, _____CHARACTER_____, "
        
    def set_postive_prompt(self, quality: str, artist: str, place: str, pose: str, character: str, node_id: str) -> None:
            self.reset_postive_prompt(node_id)
            str_prompt = str(self.nodes[node_id]["inputs"]["text"])
            str_prompt = str_prompt.replace('_____QUALITY_____', quality)
            str_prompt = str_prompt.replace('_____ARTIST_____', artist)
            str_prompt = str_prompt.replace('_____PLACE_____', place)
            str_prompt = str_prompt.replace('_____POSE_____', pose)
            str_prompt = str_prompt.replace('_____CHARACTER_____', character)
            self.nodes[node_id]["inputs"]["text"] = str_prompt
            #print('pos set!')

    def set_negative_prompt(self, negquality: str, node_id: str) -> None:
            self.nodes[node_id]["inputs"]["text"] = negquality
            #print('neg set!')                                
    
    def set_seed(self, seed: int, node_id: str) -> None:
        self.nodes[node_id]["inputs"]["int"] = seed
        print('Seed = {} set!'.format(seed))
    
    def set_width_height(self, width: int, height: int, node_id: str) -> None:
        self.nodes[node_id]["inputs"]["Width"] = width
        self.nodes[node_id]["inputs"]["Height"] = height
        print('Width = {} and Height = {} set!'.format(width, height))
        
    def set_steps_cfg(self, steps: int, cfg: float, node_id: str) -> None:              
        self.nodes[node_id]["inputs"]["steps"] = steps
        self.nodes[node_id]["inputs"]["cfg"] = cfg
        print('Steps = {} and cfg = {} set!'.format(steps, cfg))    

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = parse.urlencode(data)
        with request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())   
             
    def get_images(self, ws, prompt_id):
        print('Waiting for images...')
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            images_output = []
            if 'images' in node_output:
                print(f"Node {node_id} has {len(node_output['images'])} images")
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
        print('Waiting for images... done!')
        return images_output        

    def save_images(self, images, output_folder, random_integer):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for i, image_data in enumerate(images):
            now_time = int(time.time())
            save_image_name = f"{random_integer}_{now_time}"
            image_path = os.path.join(output_folder, f'{save_image_name}.png')
            with open(image_path, 'wb') as f:
                f.write(image_data)
            print(f'Saved image to {image_path}')
            return image_path

    def pick_image(self, images):
        for _, image_data in enumerate(images):
            return image_data

    def queue_prompt(self) -> None:
        data = json.dumps({"prompt": self.nodes, "client_id": self.client_id}).encode('utf-8')
        #print(data)
        
        req = request.Request(f"http://{self.server_address}/prompt", data=data,  headers={'Content-Type': 'application/json'})
        
        prompt_id = json.loads(request.urlopen(req).read())['prompt_id']
        print(f"Prompt queued with ID: {prompt_id}")
        
        images = self.get_images(ws, prompt_id)        
        return images

def run_comfyui(server_address, positive_prompt, negative_prompt, random_seed, steps, cfg, width, height ):
    global ws
    client_id = str(uuid.uuid4())   
    current_file_path = os.path.abspath(__file__)
    current_folder = os.path.dirname(current_file_path)
    print('current_folder='+current_folder)
                
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))            
    
    my_gen = ComfyUIAPIGenerator(server_address, client_id, current_folder+'\\workflow_api.json')                
    my_gen.set_steps_cfg(steps=steps, cfg=cfg, node_id="13")
    my_gen.set_seed(seed=random_seed, node_id="16")    
    my_gen.set_width_height(width=width, height=height, node_id="12")
    my_gen.set_postive_prompt(positive_prompt, '', '', '', '', "14")              
    my_gen.set_negative_prompt(negquality=negative_prompt, node_id="15")
    images = my_gen.queue_prompt()
        
    #image_path = my_gen.save_images(images, current_folder+'\\',random_integer)
    
    ws.close()            
        
    return my_gen.pick_image(images)

def extract_comfyui_content(text):
    pattern = '{}(.*?){}'.format(TRIGGER_LEFT, TRIGGER_RIGHT)
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def simplify_path(path):
    normalized_path = os.path.normpath(path)
    absolute_path = os.path.abspath(normalized_path)
    return absolute_path
