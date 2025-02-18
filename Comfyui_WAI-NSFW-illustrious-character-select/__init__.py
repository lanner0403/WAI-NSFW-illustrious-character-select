from .illustrious_character_select import llm_prompt_node, illustrious_character_select

def __init__(self):
    pass
    
# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "llm_prompt_node"              : llm_prompt_node,
    "illustrious_character_select" : illustrious_character_select,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {    
    "llm_prompt_node"              : "llm_prompt",
    "illustrious_character_select" : "illustrious_character_select",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

