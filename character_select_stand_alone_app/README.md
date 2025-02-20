# Character Select SAA
This is a Stand Alone App with AI prompt and ComfyUI/WebUI API support.   
------

# Install and Run
1. Copy this folder to anywhere you like   
2. Dbclick #run.bat   
3. Open your Chrome/Edge and paste `http://127.0.0.1:47861/`   
4. Have fun   
------

# AI prompt
## Remote   
1. Modify `json/wai_settings.json` to setup your API key and Model   
2. Set `AI Prompt Generator` to `Remote`   
3. Put something e.g. `make character furry, and I wang a detailed portrait` in `AI Prompt`    

## Local
1. Make sure you know how to build [Llama.cpp](https://github.com/ggml-org/llama.cpp) yourself, or download them from trusted source   
2. Download Model from [HuggingFace](https://huggingface.co/), recommend GGUF like `Llama-3.3-7B-q8`   
3. Recommend Server args `llama-server.exe -ngl 40 --no-mmap -m "<your GGUF model here>`
4. Set `AI Prompt Generator` to `Local`
5. Put something e.g. `make character furry, and I wang a detailed portrait` in `AI Prompt`
------

# API   
## ComfyUI   
1. Enable `DEV mode` in ComfyUI Settings   
2. Select `Local Image Generator API` to `ComfyUI`   
3. Make sure `Local Image Generator IP Address:Port` same as your ComfyUI page   
4. Have fun   

## WebUI
1. Enable `API mode` by add `--api` in `COMMANDLINE_ARGS` (webui-user.bat)   
2. run it   
3. Select `Local Image Generator API` to `WebUI`   
4. Make sure `Local Image Generator IP Address:Port` same as your WerUI page   
5. Have fun
------

# FAQ
You may need few supports lib for python   

```
py -m pip install gradio
py -m pip install websockets  
py -m pip install websocket-client
```


