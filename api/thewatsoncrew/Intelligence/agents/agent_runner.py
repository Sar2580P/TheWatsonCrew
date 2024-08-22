from llama_index.core.agent import AgentRunner
from typing import (
    Any,
    List,
    Optional,
    Sequence,
    Type,
    Callable,
    Union,
    Dict,
)
from collections import deque
from llama_index.core.agent.react.formatter import ReActChatFormatter
from llama_index.core.agent.react.output_parser import ReActOutputParser
from llama_index.core.agent.react.step import ReActAgentWorker
from llama_index.core.agent.runner.base import AgentRunner
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.callbacks import (
    CallbackManager,
)
from llama_index.core.agent.types import (
    Task,
)
from llama_index.core.agent.runner.base import TaskState
from llama_index.core.llms.llm import LLM
from llama_index.core.memory.chat_memory_buffer import ChatMemoryBuffer
from llama_index.core.memory.types import BaseMemory
from llama_index.core.objects.base import ObjectRetriever
from llama_index.core.tools import BaseTool, ToolOutput
from langchain.tools import BaseTool, StructuredTool
from llama_index.core.prompts.mixin import PromptMixinType
from Intelligence.dag_planner.DAG import CustomAgentExecutor
from Intelligence.dag_planner.node import Node 
from collections import deque
from Intelligence.utils.misc_utils import logger, pr
import networkx as nx
import matplotlib.pyplot as plt
import json
from langchain.agents.output_parsers.react_single_input import ReActSingleInputOutputParser
from Intelligence.dag_planner.agent import PersonalAgent
from Intelligence.utils.llm_utils import Settings, llm as langchain_llm
import os, glob

class MyAgentRunner(AgentRunner):
    def __init__(
        self,
        tools: Sequence[Union[BaseTool, 'MyAgentRunner']],
        llm: LLM,
        memory: BaseMemory,
        name:str ,
        description:str,
        max_iterations: int = 10,
        _input:str = None,
        usage_idx: int = None,
        react_chat_formatter: Optional[ReActChatFormatter] = None,
        output_parser: Optional[ReActOutputParser] = None,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
        tool_retriever: Optional[ObjectRetriever[BaseTool]] = None,
        context: Optional[str] = None,
        handle_reasoning_failure_fn: Optional[
            Callable[[CallbackManager, Exception], ToolOutput]
        ] = None,
    ) -> None:
        """Init params."""
        callback_manager = callback_manager or llm.callback_manager
        if context and react_chat_formatter:
            raise ValueError("Cannot provide both context and react_chat_formatter")
        if context:
            react_chat_formatter = ReActChatFormatter.from_context(context)

        step_engine = ReActAgentWorker.from_tools(
            tools=tools,
            tool_retriever=tool_retriever,
            llm=llm,
            max_iterations=max_iterations,
            react_chat_formatter=react_chat_formatter,
            output_parser=output_parser,
            callback_manager=callback_manager,
            verbose=verbose,
            handle_reasoning_failure_fn=handle_reasoning_failure_fn,
        )
        super().__init__(
            step_engine,
            memory=memory,
            llm=llm,
            callback_manager=callback_manager,
        )
        
        # Agent as tool:
        self.name = name
        self.description = description 
        self.usage_idx = usage_idx
        self.input = _input
        
        # DAG Planning related attributes
        self.is_single_input = True
        self.wrapped_tools = self.wrap_as_tool(tools)
        self.dag_agent_planner = PersonalAgent.from_llm_and_tools(
            llm = langchain_llm, tools = self.wrapped_tools  #, output_parser=ReActSingleInputOutputParser()
            )
        self.dag_agent_worker = CustomAgentExecutor(
                                    agent=self.dag_agent_planner ,
                                    agent_name=self.name,
                                    tools= self.wrapped_tools,
                                    verbose=True,
                                    return_intermediate_steps=True,
                                    handle_parsing_errors=True,
                                )
        
        # tool, sub-agent mapping
        self.mapping = {
            tool.name : tool for tool in tools
        }
        
        
        # re-create planning for new query
        if self.name == 'ROOT':
            files = glob.glob(os.path.join('Intelligence/dag_planner/planning', '*'))

            for file in files:
                if os.path.isfile(file):
                    os.remove(file)


    @classmethod
    def from_tools(
        cls,
        tools: Optional[List[Union[BaseTool, 'MyAgentRunner']]] = None,
        name:str = 'MyAgentRunner',
        description:str = 'AgentRunner for user assisstance',
        tool_retriever: Optional[ObjectRetriever[BaseTool]] = None,
        llm: Optional[LLM] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        memory: Optional[BaseMemory] = None,
        memory_cls: Type[BaseMemory] = ChatMemoryBuffer,
        max_iterations: int = 10,
        react_chat_formatter: Optional[ReActChatFormatter] = None,
        output_parser: Optional[ReActOutputParser] = None,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
        context: Optional[str] = None,
        handle_reasoning_failure_fn: Optional[
            Callable[[CallbackManager, Exception], ToolOutput]
        ] = None,
        **kwargs: Any,
    ) -> "MyAgentRunner":
        """Convenience constructor method from set of BaseTools (Optional).

        NOTE: kwargs should have been exhausted by this point. In other words
        the various upstream components such as BaseSynthesizer (response synthesizer)
        or BaseRetriever should have picked up off their respective kwargs in their
        constructions.

        If `handle_reasoning_failure_fn` is provided, when LLM fails to follow the response templates specified in
        the System Prompt, this function will be called. This function should provide to the Agent, so that the Agent
        can have a second chance to fix its mistakes.
        To handle the exception yourself, you can provide a function that raises the `Exception`.

        Note: If you modified any response template in the System Prompt, you should override the method
        `_extract_reasoning_step` in `ReActAgentWorker`.

        Returns:
            ReActAgent
        """
        llm = llm or Settings.llm
        if callback_manager is not None:
            llm.callback_manager = callback_manager
        memory = memory or memory_cls.from_defaults(
            chat_history=chat_history or [], llm=llm
        )
        return cls(
            tools=tools or [],
            tool_retriever=tool_retriever,
            llm=llm,
            name = name, 
            description = description,
            memory=memory,
            max_iterations=max_iterations,
            react_chat_formatter=react_chat_formatter,
            output_parser=output_parser,
            callback_manager=callback_manager,
            verbose=verbose,
            context=context,
            handle_reasoning_failure_fn=handle_reasoning_failure_fn,
        )
        
    def create_task(self, input: str, **kwargs: Any) -> Task:
        """Create task."""
        if not self.init_task_state_kwargs:
            extra_state = kwargs.pop("extra_state", {})
        else:
            if "extra_state" in kwargs:
                raise ValueError(
                    "Cannot specify both `extra_state` and `init_task_state_kwargs`"
                )
            else:
                extra_state = self.init_task_state_kwargs

        callback_manager = kwargs.pop("callback_manager", self.callback_manager)
        task = Task(
            input=input,
            memory=self.memory,
            extra_state=extra_state,
            callback_manager=callback_manager,
            **kwargs,
        )
        # # put input into memory
        # self.memory.put(ChatMessage(content=input, role=MessageRole.USER))

        # get initial step from task, and put it in the step queue
        initial_step = self.agent_worker.initialize_step(task)

        task_state = TaskState(
            task=task,
            step_queue=deque([initial_step]),
        )
        # add it to state
        self.state.task_dict[task.task_id] = task_state

        return task

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt modules."""
        return {"agent_worker": self.agent_worker}
    
    def wrap_as_tool(self, tools: List[Union[BaseTool, 'MyAgentRunner']]) -> List[BaseTool]:
        wrapped_tools = []
        def sample_func(input:str):
            pass
        for t in tools:
            if isinstance(t, MyAgentRunner):
                tool_ =  StructuredTool.from_function(
                            func=sample_func,
                            name=t.name,
                            description=t.description,
                        )
                wrapped_tools.append(tool_)
            else:
                wrapped_tools.append(t)
        return wrapped_tools
    
    def create_graph_from_nodes_json(self, json_data: Union[str, List[Dict]]) -> Dict[str, Any]:
        if isinstance(json_data, str):
            # If a path to a JSON file is provided, load the JSON data from the file
            with open(json_data, 'r') as file:
                json_data = json.load(file)
    
        instance_mapping : Dict[int, Union[Node, MyAgentRunner]] = {}
        in_graph :dict[int, List[int]]= {}
        out_graph :dict[int, List[int]]= {}
        in_deg = []
        for idx, item in enumerate(json_data):
            tool_info = item['tool']
            if 'tool' in tool_info['tool_name'].lower():
                node_instance = Node(
                    tool_name=tool_info['tool_name'],
                    tool_input=tool_info['tool_input'],
                    usage_idx=idx,
                    mapping=instance_mapping
                )
                in_graph[idx] = node_instance.parent_node_idxs
                out_graph[idx] = node_instance.children_node_idxs
                in_deg.append(len(node_instance.parent_node_idxs))
                instance_mapping[node_instance.usage_idx] = node_instance
            elif 'agent' in tool_info['tool_name'].lower():
                agent_instance:MyAgentRunner = self.mapping[tool_info['tool_name']]
                agent_instance.usage_idx = idx
                agent_instance.input = tool_info['tool_input']
                '''
                assumptions for agent : 
                - assuming agent has no children, query gets completely absorbed by the agent
                - assuming agent has no parent nodes, agent is self-sufficient to answer
                '''
                instance_mapping[agent_instance.usage_idx] = agent_instance
                in_deg.append(0)
        
        return {
            'instance_mapping' : instance_mapping ,
            'in_graph' : in_graph, 
            'out_graph' : out_graph , 
            'in_deg' : in_deg
        }
        
    def __repr__(self) -> str:
        return (
            f"MyAgentRunner("
                f"tool_name={self.name}, "
                f"tool_input={self.input}, "
                f"usage_idx={self.usage_idx}"
                f")"
        )
    
    def dag_response(self, instance_display_order:List[Node] = [],  **kwargs: Any) -> List[Node]:
        self.dag_agent_worker({'input' : self.input})
        dag_setup = self.create_graph_from_nodes_json(f'Intelligence/dag_planner/planning/{self.name}_planning.json')
        logger.debug('\n---------Filling nodes topo-bfs manner--------\n')
        # applying topo-bfs starting with nodes having 0 indegree
        deq = deque()
        
        # assuming : no-cycles present
        for i, in_deg in enumerate(dag_setup['in_deg']):
            if in_deg == 0:
                deq.append(i)

        # self.instance_display_order = []
        while len(deq)>0:
            node_idx = deq.popleft()
            
            node_instance : Union[Node, MyAgentRunner] = dag_setup['instance_mapping'][node_idx]
            if isinstance(node_instance, Node):
                node_instance.run_node()
                instance_display_order.append(node_instance)

                for child_idx in node_instance.children_node_idxs:
                    dag_setup['in_deg'][child_idx] -= 1
                    if dag_setup['in_deg'][child_idx] ==0 : 
                        deq.append(child_idx)
            else:
                # node is yet another agent_runner
                node_instance.dag_response(instance_display_order)
        
        logger.debug('\n---------Completed filling all nodes--------\n')
        return instance_display_order
    
    # def draw_dag_planning_graph(self, nodes: List[Node], **kwargs: Any):
    #     G = nx.DiGraph()

    #     for node in nodes:
    #         sanitized_tool_input = node.tool_input.replace('$', r'\$')
    #         G.add_node(node.usage_idx, label=f"Tool_Name= {node.tool_name}\n Tool_Input= {sanitized_tool_input}\nIndex= {node.usage_idx}")

    #     # Add edges to the graph based on parent-child relationships
    #     for node in nodes:
    #         for child_idx in node.children_node_idxs:
    #             G.add_edge(node.usage_idx, child_idx)

    #     # Set node positions in the graph
    #     pos = nx.spring_layout(G)

    #     # Create figure and axis
    #     fig, ax = plt.subplots(figsize=(12, 8))

    #     # Draw the nodes
    #     node_labels = nx.get_node_attributes(G, 'label')
    #     nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', node_shape='s', ax=ax)
    #     nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, verticalalignment='center', ax=ax)

    #     # Draw the edges
    #     nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, connectionstyle='arc3,rad=0.1', ax=ax)

    #     # Display the graph
    #     plt.title('Diagram of DAG Planning')
    #     plt.savefig('Intelligence/dag_planner/dag_planning_graph.png')