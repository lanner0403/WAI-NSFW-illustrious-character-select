from .illustrious_character_select import llm_prompt_gen, illustrious_character_select, illustrious_character_select_en, mira_local_llm_prompt_gen

def __init__(self):
    pass
    
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "llm_prompt_gen"              : llm_prompt_gen,
    "illustrious_character_select" : illustrious_character_select,
    "illustrious_character_select_en" : illustrious_character_select_en,
    "mira_local_llm_prompt_gen"    : mira_local_llm_prompt_gen,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {    
    "llm_prompt_gen"                : "AI Prompt Generator",
    "mira_local_llm_prompt_gen"     : "Local AI Prompt Generator (llama.cpp)",
    "illustrious_character_select"  : "WAI illustrious Character Select CN",
    "illustrious_character_select_en" : "WAI illustrious Character Select EN",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

