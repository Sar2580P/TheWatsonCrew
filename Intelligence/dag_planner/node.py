from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Union
import re
from Intelligence.utils.misc_utils import assert_, logger
from Intelligence.tools.tool_instance_mappings import tool_instance_mapping as TIM  


class Node(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to be used.")
    tool_input: str = Field(..., description="Input query to the tool, initially in raw form containing $$PREV[i].")
    usage_idx: int = Field(..., description="The index in sequence of tool calling when this tool is called by agent.")
    parent_node_idxs: List[int] = Field(default_factory=list, description="List of idx at which the parent nodes were called to access their outputs for enhancing tool input.")
    children_node_idxs: List[int] = Field(default_factory=list, description="List of idx at which children nodes are called, just to improve connectivity among nodes.")
    output: str = Field(default="", description="Initially empty, but contains final synthesized response using parent nodes and tool input.")
    metadata: Dict[str, Union[List[int], List[str]]] = Field(default_factory=dict, description="Meta-data of docs accessed from similarity search to answer query pertaining to this node.")
    mapping: Dict[int, "Node"] = Field(default_factory=dict, description="Dictionary mapping node indices to Node instances.")
    tool_emoji: str = Field(default="", description="Emoji representing the tool.")
    
    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='before')
    def initialize_parent_node_idxs(cls, values):
        tool_input = values.get('tool_input', '')
        parent_node_idxs = values.get('parent_node_idxs', [])
        # Find all occurrences of $$PREV[i]
        matches = re.findall(r'\$\$PREV\[(\d+)\]', tool_input)
        parent_node_idxs.extend(int(match) for match in matches)
        # Remove duplicates and sort
        values['parent_node_idxs'] = sorted(set(parent_node_idxs))
        
        # updating the children of parent Nodes with the current node index
        for parent_idx in parent_node_idxs:
            assert_(parent_idx in values['mapping'], f"Parent node with index {parent_idx} not found in mapping.")
            parent_node = values['mapping'][parent_idx]
            parent_node.children_node_idxs.append(values['usage_idx'])
            
        return values
    
    def __str__(self):
        return (f"Node(\n"
                f"  tool_name={self.tool_name},\t"
                f"  tool_input={self.tool_input},\t"
                f"  usage_idx={self.usage_idx},\t"
                f"  parent_node_idxs={self.parent_node_idxs},\t"
                f"  children_node_idxs={self.children_node_idxs},\t"
                f"  output = {self.output},\t"
                f"  metadata={self.metadata}\t"
                f")")
        
    def create_prompt(self):
        # Access instances of parent nodes using the mapping
        for parent_idx in self.parent_node_idxs:
            if parent_idx in self.mapping:
                parent_node = self.mapping[parent_idx]
                # Concatenate parent node output with tool_input
                self.tool_input += f" {parent_node.output}"
            else:
                raise ValueError(f"Parent node with index {parent_idx} not found in mapping.")
        return self.tool_input

    async def run_node(self):
        # Reframe the entire input query using the LLM
        # final_query_prompt = llm.reframe_query(self.create_prompt())
        final_query_prompt = self.create_prompt()
        # Call retriever to get most similar documents
        tool_output:dict = TIM[self.tool_name].run(final_query_prompt)
        self.tool_emoji = TIM[self.tool_name].emoji
        # Synthesize a final response for this node
        # synthesized_response = llm.synthesize_response(tool_output['tool_response'])
        
        # Store the output and metadata
        self.output = tool_output['tool_response']
        self.metadata = tool_output.get('response_metadata', {})
            
        return self.output, self.metadata