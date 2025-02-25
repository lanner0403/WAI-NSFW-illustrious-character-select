WAI-NSFW-illustrious-SDXL 專用角色選擇器

easy to use stable-diffusion-webui for WAI-NSFW-illustrious-SDXL https://civitai.com/models/827184?modelVersionId=1183765

相關安裝 dependence

add-detail-xl  https://huggingface.co/PvDeep/Add-Detail-XL/blob/main/add-detail-xl.safetensors

Pony: People's Works - ponyv4_noob1_2_adamW-000017  https://civitai.green/models/856285/pony-peoples-works?modelVersionId=1036362

ChihunHentai  https://civitai.com/models/106586

SDXL VAE  https://civitai.com/models/296576?modelVersionId=333245

如何安裝: 透過普通 URL 安裝即可

To install: Go to settings tab of stable-diffusion-webui, go to install from url, paste in this url and click install:

更新 !!!!!如新功能無法使用請砍掉重新安裝!!!!

2/23 調整部分預設，新增簡易手機模式

2/22 人物翻譯完成，動作部分恕我不太想翻譯(恥力不夠，不小心被人喵到不太好....)，部分prompt調整

2/20 小調整及翻譯，處理切換太快產生當機bug，新增分開的隨機按鈕

2/15 更新AI功能(預設、建議可自行申請API Key)、部分角色名稱修正、免額外下載檔案，AI使用上目前 llama-3.3-70b-versatile

1/19 更新AI功能、部分角色名稱修正、下載Timeout 延長至10分鐘

AI 功能 支援 各家API ex: groq llama-3.3-70b-versatile (免費) 

設定方式:

extensions\WAI-NSFW-illustrious-character-select\custom_settings.json

將 ai 設定為 true

並輸入 api_key (自行自 https://console.groq.com/ 申請)

ex:

    "ai": true,
    
    "base_url": "https://api.groq.com/openai/v1/chat/completions",
    
    "model": "llama-3.3-70b-versatile",
    
    "api_key":"gsk_UGQDzQaAxXrWx9ycd9OlW--------------------"
    


