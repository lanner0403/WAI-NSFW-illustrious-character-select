import base64
from cProfile import label
import io
import random
from PIL import Image
import gradio as gr
import modules.sd_samplers
import modules.scripts as scripts
from modules import shared
import json
import os
import shutil
import requests
import textwrap
from pprint import pprint
from modules.ui import gr_show
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlparse
import time


#  *********     versioning     *****
repo = "a1111"

try:
    import launch

    if not launch.is_installed("colorama"):
            launch.run_pip("install colorama")
except:
    pass

try:
    from colorama import just_fix_windows_console, Fore, Style
    just_fix_windows_console()
except:
    pass


class CharacterSelect(scripts.Script):

    BASEDIR = scripts.basedir()

    def __init__(self, *args, **kwargs):
        # components that pass through after_components
        self.all_components = []
        
        self.compinfo = namedtuple("CompInfo", ["component", "label", "elem_id", "kwargs"])

        self.settings_file = "settings.json"
        self.character_file = "character.json"
        self.action_file = "action.json"
        self.custom_settings_file = "custom_settings.json"
        self.custom_character_file = "custom_character.json"
        self.custom_action_file = "custom_action.json"

        # Read saved settings
        self.settings = self.get_config2(self.settings_file)
        self.character = self.get_config2(self.character_file)
        self.action = self.get_config2(self.action_file)
        
        self.copy_json_file(self.settings_file,self.custom_settings_file)
        self.copy_json_file(self.character_file,self.custom_character_file)
        self.copy_json_file(self.action_file,self.custom_action_file)

        try:
            self.settings = self.get_config2(self.custom_settings_file)
        except:
            print(f"錯誤：自訂設定 '{self.custom_settings_file}' 不存在")

        try:
            self.character = self.get_config2(self.custom_character_file)
        except:
            print(f"錯誤：自訂人物 '{self.custom_character_file}' 不存在")

        try:
            self.action = self.get_config2(self.custom_action_file)
        except:
            print(f"錯誤：自訂動作 '{self.custom_action_file}' 不存在")

        #設定
        self.hm_config_1 = "custom_character.json"
        self.hm_config_2 = "custom_action.json"
        #self.hm_config_7 = "wai_character.json"
        #self.hm_config_8 = "wai_character2.json"
        
        #if(self.chk_character(self.hm_config_7) == False):
            #print("角色檔1:" + self.settings["wai_json_url1"] + " 下載中")
            #self.download_json(self.settings["wai_json_url1"], os.path.join(CharacterSelect.BASEDIR, "wai_character.json"))
            #print("角色檔1 下載完成")

        #if(self.chk_character(self.hm_config_8) == False):
        #    print("角色檔2:" + self.settings["wai_json_url2"] + " 下載中")
        #    self.download_json(self.settings["wai_json_url2"], os.path.join(CharacterSelect.BASEDIR, "wai_character2.json"))
        #    print("角色檔2 下載完成")

        self.hm_config_1_component = self.get_config2(self.hm_config_1)
        #for item in self.get_character(self.hm_config_7):
        #    self.hm_config_1_component.update({item : item})
        num_parts = 10
        self.hm_config_1_img = []
        for i in range(num_parts):            
            for item in self.get_config2(f"output_{i+1}.json"):
                self.hm_config_1_img.append(item)
                #key = list(item.keys())[0]
                #self.hm_config_1_component.update({key : key})

        self.hm_config_1_img = sorted(self.hm_config_1_img, key=lambda x: list(x.keys())[0])
        for item in self.hm_config_1_img:
            key = list(item.keys())[0]
            self.hm_config_1_component.update({key : key})

        self.hm_config_2_component = self.get_config2(self.hm_config_2)

        #self.hm_config_1_img = self.get_characterimg(self.hm_config_8)
        #for item in self.get_characterimg(self.hm_config_8):
        #    self.hm_config_1_img.append(item)
        
        self.localizations = "zh_TW.json"
        self.localizations_component = self.get_config2(self.localizations)
        self.relocalizations_component = {value: key for key, value in self.localizations_component.items()}

        self.hm1prompt = ""
        self.hm2prompt = ""

        #text value
        self.hm1btntext = ""
        self.hm2btntext = ""
        self.hm3btntext = ""
        self.hm4btntext = ""

        self.locked1 = ""
        self.locked2 = ""
        self.locked3 = ""
        self.locked4 = ""
        #loading - 避免回跳
        self.loading = 0

        #隨機的face也要記下來 避免蓋掉
        self.faceprompt = ""

        self.allfuncprompt = ""

        #前一次的 cprompt
        self.oldcprompt=""

        self.elm_prfx = "characterselect"
        CharacterSelect.txt2img_neg_prompt_btn = gr.Button(
            value="使用預設值",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_neg_prompt_btn"
        )
        CharacterSelect.txt2img_prompt_btn = gr.Button(
            value="使用提詞",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_prompt_btn"
        )
        CharacterSelect.txt2img_radom_C_prompt_btn = gr.Button(
            value="人物",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_C_randomprompt_btn", 
            min_width=50
        )
        CharacterSelect.txt2img_radom_A_prompt_btn = gr.Button(
            value="動作",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_A_randomprompt_btn", 
            min_width=50
        )
        CharacterSelect.txt2img_radom_prompt_btn = gr.Button(
            value="全部隨機",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_randomprompt_btn", 
            min_width=100
        )

        #h_m 人物
        CharacterSelect.txt2img_hm1_dropdown = gr.Dropdown(
            label="人物搜尋",
            choices=list(self.hm_config_1_component.keys()),
            render = False,
            elem_id=f"{self.elm_prfx}_hm1_dd"
        )

        CharacterSelect.txt2img_hm1_slider = gr.Slider(
            minimum = 0,
            maximum = len(self.hm_config_1_component) - 1,
            value = 0,
            step = 1,
            render = False,
            elem_id=f"{self.elm_prfx}_hm1_slider"
        )

        CharacterSelect.txt2img_hmzht_dropdown = gr.Dropdown(
            label="中文人物搜尋",
            choices=list(self.localizations_component.keys()),
            render = False,
            elem_id=f"{self.elm_prfx}_hmzht_dd"
        )

        CharacterSelect.txt2img_hm1_img = gr.Image(
            width = 100
        )

        #h_m 姿勢
        CharacterSelect.txt2img_hm2_dropdown = gr.Dropdown(
            label="動作",
            choices=list(self.hm_config_2_component.keys()),
            render = False,
            elem_id=f"{self.elm_prfx}_hm2_dd"
        )

        #功能性調節
        CharacterSelect.func00_chk =gr.Checkbox(
            label="NSFW",
            render = False,
            container = False,
            elem_id=f"{self.elm_prfx}_func00_chk"
        )
        CharacterSelect.func01_chk =gr.Checkbox(
            label="增加細節",
            render = False,
            container = False,
            elem_id=f"{self.elm_prfx}_func01_chk"
        )
        CharacterSelect.func02_chk =gr.Checkbox(
            label="減少細節",
            render = False,
            container = False,
            elem_id=f"{self.elm_prfx}_func02_chk"
        )
        CharacterSelect.func03_chk = gr.Checkbox(
            label="品質加強",
            render = False,
            container = False,
            elem_id=f"{self.elm_prfx}_func03_chk"
        )
        CharacterSelect.func04_chk =gr.Checkbox(
            label="人物加強",
            render = False,
            container = False,
            elem_id=f"{self.elm_prfx}_func04_chk"
        )

        #鎖定
        CharacterSelect.txt2img_lock1_btn = gr.Button(
            value="",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_lock1_btn"
        )
        CharacterSelect.txt2img_lock2_btn = gr.Button(
            value="",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_lock2_btn"
        )
        #中文輸入框
        CharacterSelect.txt2img_cprompt_txt = gr.Textbox(lines=4, placeholder="可輸入中文描述，透過AI擴充場景", label="AI 擴充 prompt", elem_id=f"{self.elm_prfx}_cprompt_txt")
        CharacterSelect.txt2img_cprompt_btn = gr.Button(
            value="AI擴充",
            label="cpromptbtn",
            variant="primary",
            render = False,
            elem_id=f"{self.elm_prfx}_cprompt_btn"
        )

        self.input_prompt = CharacterSelect.txt2img_cprompt_txt
    
    def fakeinit(self, *args, **kwargs):
        """
        __init__ workaround, since some data is not available during instantiation, such as is_img2img, filename, etc.
        This method is called from .show(), as that's the first method ScriptRunner calls after handing some state dat (is_txt2img, is_img2img2)
        """ 
        
        self.hide_all_button = gr.Button(value="簡易版", variant="primary", render=False, visible=True, elem_id=f"{self.elm_prfx}_hide_all_bttn")
        self.show_all_button = gr.Button(value="一般版", variant="primary", render=False, visible=True, elem_id=f"{self.elm_prfx}_show_all_bttn")
        self.lock_seed_button = gr.Button(value="鎖定seed", variant="primary", render=False, visible=True, elem_id=f"{self.elm_prfx}_lock_seed_bttn")
        self.rdn_seed_button = gr.Button(value="隨機seed", variant="primary", render=False, visible=True, elem_id=f"{self.elm_prfx}_rdn_seed_bttn")

    def title(self):
        return "CharacterSelect"

    def before_component(self, component, **kwargs):
        pass
    def _before_component(self, component, **kwargs):
        # Define location of where to show up
        #if kwargs.get("elem_id") == "":#f"{'txt2img' if self.is_txt2img else 'img2img'}_progress_bar":
        #print(kwargs.get("label") == self.before_component_label, "TEST", kwargs.get("label"))
        #if kwargs.get("label") == self.before_component_label:
        with gr.Row(equal_height = True):
            CharacterSelect.txt2img_neg_prompt_btn.render()
        with gr.Accordion(label="人物動作設定", open = True, elem_id=f"{'txt2img' if self.is_txt2img else 'img2img'}_preset_manager_accordion"):
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_hm1_dropdown.render() 
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_hmzht_dropdown.render() 
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_hm1_slider.render() 
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_hm1_img.render()
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_hm2_dropdown.render() 
            with gr.Row(variant='compact'):
                CharacterSelect.txt2img_radom_C_prompt_btn.render()
                CharacterSelect.txt2img_radom_A_prompt_btn.render()
                CharacterSelect.txt2img_radom_prompt_btn.render()
        with gr.Accordion(label="其他設定", open = False, elem_id=f"{'txt2img' if self.is_txt2img else 'img2img'}_h_setting_accordion"):
            with gr.Row(equal_height = True):
                CharacterSelect.func00_chk.render()
                CharacterSelect.func01_chk.render()
                CharacterSelect.func02_chk.render()
                CharacterSelect.func03_chk.render() 
                CharacterSelect.func04_chk.render()
        if(self.settings["ai"]):
            with gr.Row(equal_height = True):
                CharacterSelect.txt2img_cprompt_txt.render()
                with gr.Row(equal_height = True):
                    CharacterSelect.txt2img_cprompt_btn.render()    

    def after_component(self, component, **kwargs):
        if hasattr(component, "label") or hasattr(component, "elem_id"):
            self.all_components.append(self.compinfo(
                                                      component=component,
                                                      label=component.label if hasattr(component, "label") else None,
                                                      elem_id=component.elem_id if hasattr(component, "elem_id") else None,
                                                      kwargs=kwargs
                                                     )
                                      )

        label = kwargs.get("label")
        ele = kwargs.get("elem_id")

        # 提示詞
        if ele == "txt2img_prompt": 
            self.prompt_component = component
        if ele == "txt2img_neg_prompt": 
            self.neg_prompt_component = component
        if ele == "txt2img_steps": 
            self.steps_component = component
        if ele == "txt2img_height": 
            self.height_component = component
        if ele == "txt2img_width": 
            self.width_component = component
            

        if ele == "txt2img_generation_info_button" or ele == "img2img_generation_info_button":
            self._ui()

        if ele == "txt2img_styles_dialog":
            self._before_component("")

    def ui(self, *args):
        pass

    def _ui(self):
        # Conditional for class members
        if self.is_txt2img:
            #色色大師功能區
            CharacterSelect.txt2img_prompt_btn.click(
                fn=self.fetch_valid_values_from_prompt,
                outputs=self.prompt_component
            )
            CharacterSelect.txt2img_neg_prompt_btn.click(
                fn=self.fetch_neg_prompt,
                outputs=[self.neg_prompt_component,self.steps_component,self.height_component,self.width_component,self.func00_chk,self.func01_chk,self.func03_chk,self.func04_chk]
            )
            #hm
            CharacterSelect.txt2img_hm1_dropdown.change(
                fn=self.hm1_setting,
                inputs=[CharacterSelect.txt2img_hm1_dropdown,self.prompt_component],
                outputs=[CharacterSelect.txt2img_hm1_img, self.prompt_component,CharacterSelect.txt2img_hm1_slider,CharacterSelect.txt2img_hmzht_dropdown]
            )
            CharacterSelect.txt2img_hmzht_dropdown.change(
                fn=self.hmzht_setting,
                inputs=[CharacterSelect.txt2img_hmzht_dropdown],
                outputs=[CharacterSelect.txt2img_hm1_dropdown]
            )
            CharacterSelect.txt2img_hm1_slider.release(
                fn=self.hm1_setting2,
                inputs=[CharacterSelect.txt2img_hm1_slider,self.prompt_component],
                outputs=[CharacterSelect.txt2img_hm1_dropdown]
            )
            CharacterSelect.txt2img_hm2_dropdown.change(
                fn=self.hm2_setting,
                inputs=[CharacterSelect.txt2img_hm2_dropdown, self.prompt_component],
                outputs=[CharacterSelect.txt2img_hm2_dropdown, self.prompt_component]
            )
            
            #細節功能
            detailinput = [self.prompt_component,CharacterSelect.func00_chk,CharacterSelect.func01_chk,CharacterSelect.func02_chk,CharacterSelect.func03_chk,CharacterSelect.func04_chk]
            CharacterSelect.func00_chk.change(
                fn=self.func_setting,
                inputs=detailinput,
                outputs=self.prompt_component
            )
            CharacterSelect.func01_chk.change(
                fn=self.func_setting,
                inputs=detailinput,
                outputs=self.prompt_component
            )
            CharacterSelect.func02_chk.change(
                fn=self.func_setting,
                inputs=detailinput,
                outputs=self.prompt_component
            )
            CharacterSelect.func03_chk.change(
                fn=self.func_setting,
                inputs=detailinput,
                outputs=self.prompt_component
            )
            CharacterSelect.func04_chk.change(
                fn=self.func_setting,
                inputs=detailinput,
                outputs=self.prompt_component
            )
            #鎖定
            #CharacterSelect.txt2img_lock1_btn.click(
            #    fn=self.prompt_lock1,
            #    outputs=[CharacterSelect.txt2img_hm1_dropdown, CharacterSelect.txt2img_lock1_btn]
            #) 
            #CharacterSelect.txt2img_lock2_btn.click(
            #    fn=self.prompt_lock2,
            #    outputs=[CharacterSelect.txt2img_hm2_dropdown, CharacterSelect.txt2img_lock2_btn]
            #)
            CharacterSelect.txt2img_radom_C_prompt_btn.click(
                fn=self.h_m_random_C_prompt,
                outputs=[self.prompt_component, CharacterSelect.txt2img_hm1_dropdown]
            )
            CharacterSelect.txt2img_radom_A_prompt_btn.click(
                fn=self.h_m_random_A_prompt,
                outputs=[self.prompt_component,CharacterSelect.txt2img_hm2_dropdown]
            )
            CharacterSelect.txt2img_radom_prompt_btn.click(
                fn=self.h_m_random_prompt,
                outputs=[self.prompt_component, CharacterSelect.txt2img_hm1_dropdown,CharacterSelect.txt2img_hm2_dropdown]
            )
            CharacterSelect.txt2img_cprompt_btn.click(
                fn=self.cprompt_send,
                inputs=[self.prompt_component, self.input_prompt],
                outputs=self.prompt_component
            )  


    def f_b_syncer(self):
        """
        ?Front/Backend synchronizer?
        Not knowing what else to call it, simple idea, rough to figure out. When updating choices on the front-end, back-end isn't updated, make them both match
        https://github.com/gradio-app/gradio/discussions/2848
        """
        self.inspect_dd.choices = [str(x) for x in self.all_components]
        return [gr.update(choices=[str(x) for x in self.all_components]), gr.Button.update(visible=False)]

    
    def inspection_formatter(self, x):
        comp = self.all_components[x]
        text = f"Component Label: {comp.label}\nElement ID: {comp.elem_id}\nComponent: {comp.component}\nAll Info Handed Down: {comp.kwargs}"
        return text


    def run(self, p, *args):
        pass

    def get_config(self, path, open_mode='r'):
        file = os.path.join(CharacterSelect.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict 
    
    def get_config2(self, path, open_mode='r'):
        file = os.path.join(CharacterSelect.BASEDIR, path)
        try:
            with open(file, open_mode, encoding='utf-8') as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return as_dict

    def chk_character(self, path, open_mode='r'):
        file = os.path.join(CharacterSelect.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                return True
        except FileNotFoundError as e:
           return False
    
    def get_character(self, path, open_mode='r'):
        file = os.path.join(CharacterSelect.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return [item["title"] for item in as_dict["proj"]]
    
    def get_characterimg(self, path, open_mode='r'):
        file = os.path.join(CharacterSelect.BASEDIR, path)
        try:
            with open(file, open_mode) as f:
                as_dict = json.load(f) 
        except FileNotFoundError as e:
            print(f"{e}\n{file} not found, check if it exists or if you have moved it.")
        return [{item["title"]:item["image"]} for item in as_dict["proj"]]
    
    #自訂提詞
    def fetch_valid_values_from_prompt(self):
        self.prompt_component.value = ""
        self.prompt_component.value += self.hm1prompt
        self.prompt_component.value += self.hm2prompt
        self.prompt_component.value += self.allfuncprompt
        return self.prompt_component.value
    
    #預設
    def fetch_neg_prompt(self):
        self.neg_prompt_component.value = self.settings["neg_prompt"]
        self.steps_component.value = self.settings["steps"]
        self.height_component.value = self.settings["height"]
        self.width_component.value = self.settings["width"]
        return [self.neg_prompt_component.value,self.steps_component.value,self.height_component.value,self.width_component.value,True,True,True,True]
    

    #隨機人
    def h_m_random_C_prompt(self):
        self.prompt_component.value = ""
        self.hm1btntext = list(self.hm_config_1_component)[random.randint(1,len(self.hm_config_1_component)-1)]
        self.prompt_component.value += self.hm_config_1_component[self.hm1btntext] + ","
        self.prompt_component.value += self.hm2btntext + ","
        self.prompt_component.value += self.allfuncprompt

        return [self.prompt_component.value, self.hm1btntext]

    #隨機
    def h_m_random_A_prompt(self):
        self.prompt_component.value = ""
        self.hm2btntext = list(self.hm_config_2_component)[random.randint(1,len(self.hm_config_2_component)-1)]
        self.prompt_component.value += self.hm1btntext + ","
        self.prompt_component.value += self.hm_config_2_component[self.hm2btntext] + ","
        self.prompt_component.value += self.allfuncprompt

        return [self.prompt_component.value, self.hm2btntext]

    #隨機
    def h_m_random_prompt(self):
        self.prompt_component.value = ""
        self.hm1btntext = list(self.hm_config_1_component)[random.randint(1,len(self.hm_config_1_component)-1)]
        self.hm2btntext = list(self.hm_config_2_component)[random.randint(1,len(self.hm_config_2_component)-1)]
        self.prompt_component.value += self.hm_config_1_component[self.hm1btntext] + ","
        self.prompt_component.value += self.hm_config_2_component[self.hm2btntext] + ","
        self.prompt_component.value += self.allfuncprompt

        return [self.prompt_component.value, self.hm1btntext, self.hm2btntext]
    
    #自訂1
    async def hm1_setting(self, selection, oldprompt):
        if(self.loading>=1):
            return
        self.loading = 1
        try:
            if(selection == ""):
                selection = "random"
            oldhmprompt = self.hm1prompt
            self.hm1prompt = ""
            btntext = ""
            #自行異動
            if(self.hm1btntext != selection):
                self.locked1 = ""
                if(selection != "random"):
                    self.hm1prompt = selection + ","
                    self.hm1btntext = selection
            else:
                if(selection != "random"):
                    self.hm1prompt = selection + ","
        
            if(oldhmprompt!=""):
                oldprompt = oldprompt.replace(", ",",").replace(oldhmprompt.replace(", ",","), self.hm1prompt)
            else:
                oldprompt += "," + self.hm1prompt
        
            value = "data:image/jpeg;base64,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"
            index = 0
            i=0
            for item in self.hm_config_1_img:
                i+=1
                if(item.get(selection,'') != ''):
                    value = item.get(selection)
                    index = i

            #self.base64_to_pil(self.hm_config_1_img[0].get('hatsune miku'))
        
            return [self.base64_to_pil(value), oldprompt, index, self.relocalizations_component[self.hm1btntext]]
        except:
            return
        finally:
            time.sleep(0.5)
            self.loading=0
    
    def hm1_setting2(self, selection, oldprompt):
        if(self.loading>=1):
            return
        self.loading=1
        try:
            return list(self.hm_config_1_component.keys())[selection]
        finally:
            time.sleep(0.5)
            self.loading=0

    def hmzht_setting(self, selection, oldprompt):
        if(self.loading>=1):
            return
        self.loading=1
        try:
            return self.localizations_component[selection]
        finally:
            time.sleep(0.5)
            self.loading=0
     

    #自訂2
    def hm2_setting(self, selection, oldprompt):
        if(selection == ""):
            selection = "random"
        oldhmprompt = self.hm2prompt
        self.hm2prompt = ""
        btntext = ""
        #自行異動
        if(self.hm2btntext != selection):
            self.locked2 = ""
            if(selection != "random"):
                self.hm2prompt = self.hm_config_2_component[selection] + ","
        else:
            if(selection != "random"):
                self.hm2prompt = self.hm_config_2_component[selection] + ","
            
        self.hm2btntext = selection
        if(oldhmprompt!=""):
            oldprompt = oldprompt.replace(oldhmprompt, self.hm2prompt)
        else:
            oldprompt += "," + self.hm2prompt
        
        return [selection, oldprompt]

    #細節
    def func_setting(self, oldprompt,fv0,fv1,fv2,fv3,fv4):
        self.allfuncprompt = ""
        oldprompt = oldprompt.replace(self.settings["nsfw"], "")
        oldprompt = oldprompt.replace(self.settings["more_detail"], "")
        oldprompt = oldprompt.replace(self.settings["less_detail"], "")
        oldprompt = oldprompt.replace(self.settings["quality"], "")
        oldprompt = oldprompt.replace(self.settings["character_enhance"], "")
        if(fv0):
            self.allfuncprompt += self.settings["nsfw"]
        if(fv1):
            self.allfuncprompt += self.settings["more_detail"]
        if(fv2):
            self.allfuncprompt += self.settings["less_detail"]
        if(fv3):
            self.allfuncprompt += self.settings["quality"]
        if(fv4):
            self.allfuncprompt += self.settings["character_enhance"]
        oldprompt += self.allfuncprompt
        return oldprompt
    
    def prompt_lock1(self):
        if(self.locked1 == ""):
            self.locked1 = "Y"
            self.hm1prompt = self.hm1btntext
            try:
                btntext = "鎖定:" + self.relocalizations_component[self.hm1btntext]
            except:
                btntext = "鎖定:" + self.hm1btntext
        else:
            self.locked1 = ""
            try:
                btntext = self.relocalizations_component[self.hm1btntext]
            except:
                btntext = self.hm1btntext
            self.hm1prompt = ""
        return [self.hm1prompt, btntext]
    
    def prompt_lock2(self):
        if(self.locked2 == ""):
            self.locked2 = "Y"
            self.hm2prompt = self.hm2btntext
            try:
                btntext = "鎖定:" + self.relocalizations_component[self.hm2btntext]
            except:
                btntext = "鎖定:" + self.hm2btntext
        else:
            self.locked2 = ""
            btntext = self.hm2prompt
            self.hm2prompt = ""
        return [self.hm2prompt, btntext]
    
    def cprompt_send(self, oldprompt, input_prompt):
        generated_texts = []
        generated_texts = self.send_request(input_prompt)
        #clear beafore
        oldprompt = oldprompt.replace(self.oldcprompt, '')
        self.oldcprompt = ''
        for text in generated_texts:
            self.oldcprompt += text
        self.oldcprompt = self.oldcprompt.replace(", ", ",") 
        oldprompt = oldprompt + ',' + self.oldcprompt
        print(f"llama3: {self.oldcprompt}")
        return oldprompt
    
    def send_request(self, input_prompt, **kwargs):
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
                'model': self.settings["model"],
                'messages': [
                    {"role": "system", "content": prime_directive},
                    {"role": "user", "content": input_prompt + ";Response in English"}
                ],  
            }
        headers = kwargs.get('headers', {"Content-Type": "application/json", "Authorization": "Bearer " + self.settings["api_key"]})
        base_url = self.settings["base_url"]
        response = requests.post(base_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            return []

    def local_request_restart(self):
        "Restart button"
        shared.state.interrupt()
        shared.state.need_restart = True

    def base64_to_pil(self, base64_str):
        """將 base64 字串轉換為 PIL Image"""
        if "base64," in base64_str:  # 處理 data URL 格式
            base64_str = base64_str.split("base64,")[1]
    
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return image
    
    def copy_json_file(self, source_path: str, destination_path: str, overwrite: bool = False):
        """
        複製JSON檔案並確認其格式正確
        Parameters:
        source_path (str): 來源JSON檔案的路徑
        destination_path (str): 目標位置的路徑
        overwrite (bool): 若為True則覆寫已存在的檔案，預設為False
        Returns:
        bool: 複製成功返回True，失敗返回False
        """
        try:
            # 確認來源檔案存在
            file = Path(os.path.join(CharacterSelect.BASEDIR, source_path))
            if not file.exists():
                print(f"錯誤：來源檔案 '{source_path}' 不存在")
                return False
            
            # 檢查目標檔案是否已存在
            dest = Path(os.path.join(CharacterSelect.BASEDIR, destination_path))
            if dest.exists() and not overwrite:
                return False
            
            # 讀取並驗證JSON格式
            #with open(file, 'r', encoding='utf-8') as file:
            #    json.load(file)  # 確認JSON格式正確
            
            # 建立目標資料夾（如果不存在）
            #dest.parent.mkdir(parents=True, exist_ok=True)
            
            # 複製檔案
            shutil.copy2(os.path.join(CharacterSelect.BASEDIR, source_path), os.path.join(CharacterSelect.BASEDIR, destination_path))
            print(f"成功：檔案已複製到 '{dest}'")
            return True
        
        except json.JSONDecodeError:
            print(f"錯誤：'{source_path}' 不是有效的JSON檔案")
            return False
        except Exception as e:
            print(f"錯誤：複製過程發生問題 - {str(e)}")
            return False
        
    def download_json(self, url, output_path, timeout:int=600):
        """
        從網址下載 JSON 檔案並儲存
    
        Parameters:
        url (str): JSON 檔案的網址
        output_path (str): 儲存檔案的路徑
        headers (dict): 自訂的 HTTP headers
        timeout (int): 請求超時時間（秒）
    
        Returns:
        tuple: (下載的數據, 儲存路徑)
        """
        try:
            # 設定預設 headers
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # 發送請求
            response = requests.get(url, headers=default_headers, timeout=timeout)
            response.raise_for_status()  # 檢查是否請求成功
        
            # 嘗試解析 JSON
            data = response.json()
        
            # 儲存檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except requests.exceptions.RequestException as e:
            print(f"下載發生錯誤: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤: {str(e)}")
            raise
        except Exception as e:
            print(f"發生未預期的錯誤: {str(e)}")
            raise


