class PresetManagerDropdownComponent{
    constructor(component){
        this.component = gradioApp().getElementById(component)
    }
    updateDropdown(selection){
        //getElementById("preset-util_preset_ds_dd").querySelector("select").querySelectorAll("option")[1].selected = true;
        //Array.from(this.component.querySelector("select").querySelectorAll("option")).find( e => e.value.includes(selection)).selected = true;
        this.getDropDownOptions().find( e => e.value.includes(selection)).selected = true;
        this.component.querySelector("select").dispatchEvent(new Event("change"));
    }
    getDropDownOptions(asValues=false){
        if (asValues){
            let temp = new Array;
            Array.from(this.component.querySelector("select").querySelectorAll("option")).forEach( opt => temp.push(opt.value))
            return temp
        }
        else{
            return Array.from(this.component.querySelector("select").querySelectorAll("option"))
        }
    }
    getCurrentSelection(){
        return this.component.querySelector("select").value
    }
}

class PresetManagerCheckboxGroupComponent{
    constructor(component){
        this.component = gradioApp().getElementById(component);
        this.checkBoxes = new Object;
        this.setCheckBoxesContainer()
    }
    setCheckBoxesContainer(){
        Array.from(this.component.querySelectorAll("input")).forEach( _input => this.checkBoxes[_input.nextElementSibling.innerText] = _input)
    }
    getCheckBoxes(){
        let response = new Array;
        for (let _component in this.checkBoxes){
            response.push([_component, this.checkBoxes[_component]])
        }
        return response
    }
    setCheckBoxesValues(iterable){
        for (let _componentText in this.checkBoxes){
            this.conditionalToggle(false, this.checkBoxes[_componentText])
        }
        if (iterable instanceof Array){
            setTimeout( () =>
            iterable.forEach( _label => this.conditionalToggle(true, this.checkBoxes[_label])),
            2)
        }
    }
    conditionalToggle(desiredVal, _component){
        //This method behaves like 'set this value to this'
        //Using element.checked = true/false, does not register the change, even if you called change afterwards,
        //  it only sets what it looks like in our case, because there is no form submit, a person then has to click on it twice.
        //Options are to use .click() or dispatch an event
        if (desiredVal != _component.checked){
            _component.dispatchEvent(new Event("change"))//using change event instead of click, in case browser ad-blockers blocks the click method
        }
    }
}
class PresetManagerMover{
    constructor(self, target, onLoadHandler){
        this.presetManager = gradioApp().getElementById(self)
        this.target = gradioApp().getElementById(target)
        this.handler = gradioApp().getElementById(onLoadHandler)
    }
    move(adjacentAt='afterend'){
        /*
        'beforebegin'
            <ele>
            'afterbegin'
                <otherele>
            'beforeend'
            </ele>
        'afterend'
        */
         
        this.target.insertAdjacentElement(adjacentAt, this.presetManager)
    }
    updateTarget(new_target){
        this.target = gradioApp().getElementById(new_target)
    }
}

setTimeout(() => {
    document.getElementById("preset-v_hide_all_bttn").addEventListener("click", sethideall);
    document.getElementById("preset-v_show_all_bttn").addEventListener("click", setshowall);
    document.getElementById("preset-v_lock_seed_bttn").addEventListener("click", setlockseed);
    document.getElementById("preset-v_rdn_seed_bttn").addEventListener("click", setrdnseed);
    //不使用直接產生
    //document.getElementById("preset-v_randomprompt_btn").addEventListener("click", startgenerate);
}, 10000);

setTimeout(() => {
    if(window.innerWidth < 800){
        document.getElementById("preset-v_hide_all_bttn").click();
        document.getElementById("preset-v_Preset1_btn").click();
    }
}, 10100);

function sethideall(){
    document.getElementById("txt2img_settings").style="display:none !important";
    document.getElementById("setting_sd_vae").style="display:none";
    document.getElementById("refresh_sd_vae").style="display:none";
    document.getElementById("setting_CLIP_stop_at_last_layers").style="display:none";
    document.getElementById("txt2img_neg_prompt").style="display:none";
    document.getElementById("phystonPrompt_txt2img_neg_prompt").style="display:none";
    document.getElementById("txt2img_tools").style="display:none";
    document.getElementById("txt2img_styles_row").style="display:none";
    try{
        document.getElementById("component-61").style="";
        document.getElementById("component-63").style="";
        document.getElementById("component-65").style="";
        document.getElementById("component-67").style="";
        document.getElementById("component-69").style="";
        document.getElementById("component-3301").style="";
    } catch(e){
        //alert(e);
    }
}

function setshowall(){
    document.getElementById("txt2img_settings").style="flex-grow: 1;min-width: min(320px, 100%);";
    document.getElementById("setting_sd_vae").style="";
    document.getElementById("refresh_sd_vae").style="";
    document.getElementById("setting_CLIP_stop_at_last_layers").style="";
    document.getElementById("txt2img_neg_prompt").style="";
    document.getElementById("phystonPrompt_txt2img_neg_prompt").style="";
    document.getElementById("txt2img_tools").style="";
    document.getElementById("txt2img_styles_row").style="";
    document.getElementById("component-69").style="";
    document.getElementById("component-61").style="";
    document.getElementById("component-3301").style="";
}

function setlockseed(){
    document.getElementById("txt2img_reuse_seed").click();
}

function setrdnseed(){
    document.getElementById("txt2img_random_seed").click();
}

var loadingtime = 5000;

function startgenerate(){
    document.getElementById("txt2img_generate").innerText = "等待中";
    setTimeout(() => {
        loadingtime = 2000
        document.getElementById("txt2img_generate").click();
        document.getElementById("txt2img_generate").innerText = "產生";
    }, loadingtime);
}

//function move(){
//        let src = gradioApp().getElementById("txt2img_preset_manager_accordion");
//        //let target = Array.from(gradioApp().querySelectorAll("div")).filter( d => d.hasAttribute("class") ? d.getAttribute("class").split(" ")[0] == "gradio-container": false)[0]
//        //target.insertAdjacentElement("afterbegin", src)
//        let target = gradioApp().getElementById("tab_txt2img");
//}
//document.addEventListener("DOMContentLoaded",() => () => {setTimeout(move, 10000)})

//onUiTabChange( function (...x) {console.log(x)})