import base64
import requests
import io
from PIL import Image

def run_webui(
    server_address = "http://127.0.0.1:7860",
    positive_prompt = 'miqo\'te',negative_prompt = 'nsfw', random_seed = -1, steps= 20, cfg = 7, 
    my_sampler_name='Euler a', height = 512, width = 512, 
    ):
        
    payload = {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "sampler_index": my_sampler_name,
        "scheduler": 'Automatic',
        "seed": random_seed,
        "cfg_scale": cfg,
        "save_images": True,
    }

    response = requests.post(url=f'http://{server_address}/sdapi/v1/txt2img', json=payload)
    if response.status_code != 200:
        print('Failed to connect to server, error code: {}'.format(response.status_code))
        return None
    
    res = response.json()
    out_image = Image.open(io.BytesIO(base64.b64decode(res["images"][0])))    

    if out_image:        
        return out_image
    
    return None

