from langchain.agents.agent import *
from langchain.agents import AgentExecutor
from langchain.agents.loading import AGENT_TO_CLASS
import json
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.output_parsers import OutputFixingParser
from Intelligence.utils.misc_utils import logger, assert_, pr
# agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
# agent_cls = AGENT_TO_CLASS[agent]
# agent_obj = agent_cls.from_llm_and_tools(
#             llm, task_tools,  
#         )

class CustomAgentExecutor(AgentExecutor):
    return_schema :List[Dict] = []   # added by me
    tool_count : int = 0             # added by me
    thought_execution_chain : List[Dict] = []   # added by me
    tool_gate : int = 0
    web_schema: List[Dict] = []
    agent: ZeroShotAgent
    agent_name:str
    #_______________________________________________________________________________________________
    def _call(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:

        """Run text through and get agent response."""
        if self.tool_count == 0:        
            self.return_schema = []        
            intermediate_steps = []   
            self.thought_execution_chain = []  
            self.web_schema = []  
                                
        
        # Construct a mapping of tool name to tool for easy lookup
        name_to_tool_map = {tool.name: tool for tool in self.tools}
        # We construct a mapping from each tool to a color, used for logging.
        color_mapping = get_color_mapping(
            [tool.name for tool in self.tools], excluded_colors=["green", "red"]
        )
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed

        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()
        
        # updating the prompt with the user query
        self.agent.llm_chain.prompt = self.agent.create_prompt(tools = self.tools, 
                                                               user_query=inputs['input'])

        while self._should_continue(iterations, time_elapsed):
            
            next_step_output = self._take_next_step(
                                                    name_to_tool_map,
                                                    color_mapping,
                                                    inputs,
                                                    intermediate_steps,
                                                    run_manager=run_manager,
                                                )
            if next_step_output == None:
                continue
            

            if isinstance(next_step_output, AgentFinish):
                self.tool_count = 0       
                with open (f'../Intelligence/dag_planner/planning/{self.agent_name}_planning.json' , 'w') as f:
                    json.dump(self.web_schema , f)      
                return self._return(
                    next_step_output, intermediate_steps, run_manager=run_manager
                )
            
            self.tool_count += 1        
            intermediate_steps.extend(next_step_output)
            if len(next_step_output) == 1:
                next_step_action = next_step_output[0]
                # See if tool should return directly
                tool_return = self._get_tool_return(next_step_action)
                if tool_return is not None:
                    return self._return(
                        tool_return, intermediate_steps, run_manager=run_manager
                    )
            iterations += 1
            time_elapsed = time.time() - start_time
        output = self.agent.return_stopped_response(
            self.early_stopping_method, intermediate_steps, **inputs
        )        
        
        return self._return(output, intermediate_steps, run_manager=run_manager)
    ## _______________________________________________________________________________________________
    # def _check_if_answerable_with_tools(self , query:str) -> bool:
    #     is_query_valid = llm_critique.run({'query' : query , 'tools' : "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])})
    #     print('CRITIQUE : ' , is_query_valid)
    #     output = None
    #     try : 
    #         output = critique_parser.parse(is_query_valid)
    #     except OutputParserException as e:
    #         new_parser = OutputFixingParser.from_llm(parser=critique_parser, llm=llm)
    #         output = new_parser.parse(is_query_valid)

    #     if int(output['answer']) ==1 :
    #         return True, output['reason']
    #     else :
    #         return False, output['reason']
    #_________________________________________________________________________________________________

    def _return(
        self,
        output: AgentFinish,
        intermediate_steps: list,
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        if run_manager:
            run_manager.on_agent_finish(output, color="green", verbose=self.verbose)
        final_output = output.return_values
        if self.return_intermediate_steps:
            final_output["intermediate_steps"] = intermediate_steps
        return final_output
    #_______________________________________________________________________________________________
    def _take_next_step(
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
        """Take a single step in the thought-tool-observation loop.

        Override this to take control of how the agent makes and acts on choices.
        """
        try:
            intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

            # Call the LLM to see what to do.
            output = self.agent.plan(
                intermediate_steps,
                callbacks=run_manager.get_child() if run_manager else None,
                **inputs,
            )
            if isinstance(output, AgentFinish):
                return output

            if output.tool == "NONE":
                output = AgentFinish(return_values = {'output':'Agent trying to use more tools than in ground truth.\nHence, Aborting Agent Execution ...'} ,
                                         log ='I now know the final answer.\nFinal Answer : Consecutive same tool calls , so aborting thought...')
                self.thought_execution_chain.append(output.log)
            
        except OutputParserException as e:
            pr.yellow(f'Output Parser Exception : {e}')
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise ValueError(
                    "An output parsing error occurred. "
                    "In order to pass this error back to the agent and have it try "
                    "again, pass `handle_parsing_errors=True` to the AgentExecutor. "
                    f"This is the error: {str(e)}"
                )
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                if e.send_to_llm:
                    observation = str(e.observation)
                    text = str(e.llm_output)
                else:
                    observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                raise ValueError("Got unexpected type of `handle_parsing_errors`")
            output = AgentAction("_Exception", observation, text)
            if run_manager:
                run_manager.on_agent_action(output, color="green")
            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            observation = ExceptionTool().run(
                output.tool_input,
                verbose=self.verbose,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )
            return [(output, observation)]
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output
        
        actions: List[AgentAction]
        if isinstance(output, AgentAction):
            actions = [output]
        else:
            actions = output
        result = []
        for agent_action in actions:
            if run_manager:
                run_manager.on_agent_action(agent_action, color="green")
            # Otherwise we lookup the tool
            if agent_action.tool in name_to_tool_map:
                tool = name_to_tool_map[agent_action.tool]
                return_direct = tool.return_direct
                color = color_mapping[agent_action.tool]
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                if return_direct:
                    tool_run_kwargs["llm_prefix"] = ""
                # We then call the tool on the tool input to get an observation
                tool_output = tool.run(
                    agent_action.tool_input,
                    verbose=False,
                    color=color,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
                observation = f"$$PREV[{self.tool_count}]"
               
                #==============================================================================================================
                tool_schema = {   
                    'tool_input' : agent_action.tool_input ,
                    'tool_name': tool.name,
                    'tool_usage_idx' : self.tool_count,
                    'tool_output': observation,    
                       
                }
                web_schema = {      
                    'tool': {
                        'thought' : output.log.split('\n')[0] ,
                        'tool_input' : agent_action.tool_input ,
                        'tool_name': tool.name,
                        'tool_usage_idx' : self.tool_count,
                        'tool_output': observation,
                    }                 
                }

                self.return_schema.append(tool_schema)
                self.web_schema.append(web_schema)

                #==============================================================================================================

            else:
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                observation = InvalidTool().run(
                    {
                        "requested_tool_name": agent_action.tool,
                        "available_tool_names": list(name_to_tool_map.keys()),
                    },
                    verbose=self.verbose,
                    color=None,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
            result.append((agent_action, observation))
        return result
    
    

#____________________________________________________________________________________________________


# a =  agent_executor({"input":'Get all work items similar to TKT-123, summarize them, create issues from that summary, and prioritize them '})
# a =  agent_executor({"input":'Summarise work item TKT-123'})

# print(a)
