setTimeout(() => {
    if(window.innerWidth < 800){
        sethideall();
    }
}, 10100);

function sethideall(){
    document.getElementById("txt2img_settings").style="display:none !important";
    document.getElementById("txt2img_neg_prompt").style="display:none";
    document.getElementById("characterselect_cprompt_txt").style="display:none";
    document.getElementById("characterselect_cprompt_btn").style="display:none";
}

