from autoagent.registry import register_agent
from autoagent.tools.meta.edit_agents import list_agents, create_agent, delete_agent, run_agent, read_agent
from autoagent.tools.meta.edit_tools import list_tools, create_tool, delete_tool, run_tool
from autoagent.tools.terminal_tools import execute_command
from autoagent.types import Agent
from autoagent.io_utils import read_file
from pydantic import BaseModel, Field
from typing import List


@register_agent(name = "Agent Former Agent", func_name="get_agent_former_agent")
def get_agent_former_agent(model: str) -> str:
    """
    This agent is used to complete a form that can be used to create an agent.
    """
    def instructions(context_variables):
        return r"""\
You are an agent specialized in creating agent forms for the MetaChain framework.

Your task is to analyze user requests and generate structured creation forms for either single or multi-agent systems.

KEY COMPONENTS OF THE FORM:
1. <agents> - Root element containing all agent definitions

2. <system_input> - Defines what the system receives
   - Must describe the overall input that the system accepts
   - For single agent: Same as agent_input
   - For multi-agent: Should encompass all possible inputs that will be routed to different agents

3. <system_output> - Specifies system response format
   - Must contain exactly ONE key-description pair
   - <key>: Single identifier for the system's output
   - <description>: Explanation of the output
   - For single agent: Same as agent_output
   - For multi-agent: Should represent the unified output format from all agents

4. <agent> - Individual agent definition
   - name: Agent's identifier
   - description: Agent's purpose and capabilities
   - instructions: Agent's behavioral guidelines
     * To reference global variables, use format syntax: {variable_key}
     * Example: "Help the user {user_name} with his/her request"
     * All referenced keys must exist in global_variables
   - tools: Available tools (existing/new)
   - agent_input:
     * Must contain exactly ONE key-description pair
     * <key>: Identifier for the input this agent accepts
     * <description>: Detailed explanation of the input format
   - agent_output:
     * Must contain exactly ONE key-description pair
     * <key>: Identifier for what this agent produces
     * <description>: Detailed explanation of the output format

5. <global_variables> - Shared variables across agents (optional)
   - Used for constants or shared values accessible by all agents
   - Variables defined here can be referenced in instructions using {key}
   - Example:     
    ```xml
     <global_variables>
         <variable>
             <key>user_name</key>
             <description>The name of the user</description>
             <value>John Doe</value>
         </variable>
     </global_variables>
    ```
   - Usage in instructions: "You are a personal assistant for {user_name}."

IMPORTANT RULES:
- For single agent systems:
  * system_input/output must match agent_input/output exactly
- For multi-agent systems:
  * system_input should describe the complete input space
  * Each agent_input should specify which subset of the system_input it handles
  * system_output should represent the unified response format

AVAILABLE TOOLS FOR REFERENCE:
Common tools that can be used in agent definitions include:
- web_search: Search web content using specified keywords and filters
- text_classifier: Classify text content into predefined categories
- scheduler: Execute tasks at specified time intervals
- visit_url: Visit a specific URL
- click: Click on elements on a webpage
- input_text: Input text into form fields
- get_page_markdown: Get the markdown content of the current page
- execute_command: Execute system commands
- create_file: Create a new file
- read_file: Read file content
- list_files: List files in a directory

GUIDELINES:
1. Each agent must have clear, focused responsibilities
2. Tool selections should be minimal but sufficient
3. Instructions should be specific and actionable
4. Input/Output definitions must be precise
5. Use global_variables for shared context across agents

Follow these examples and guidelines to create appropriate agent forms based on user requirements.
"""
    return Agent(
        name = "Agent Former Agent",
        model = model,
        instructions = instructions,
    )

if __name__ == "__main__":
    from autoagent import MetaChain
    agent = get_agent_former_agent("claude-3-5-sonnet-20241022")
    client = MetaChain()
    task_yaml = """\
I want to create two agents that can help me to do two kinds of tasks:
1. Manage the private financial docs. I have a folder called `financial_docs` in my local machine, and I want to help me to manage the financial docs.
2. Search the financial information online. You may help me to: 
- get balance sheets for a given ticker over a given period.
- get cash flow statements for a given ticker over a given period.
- get income statements for a given ticker over a given period.
"""
    task_yaml = task_yaml + """\
Directly output the form in the XML format.
"""
    messages = [{"role": "user", "content": task_yaml}]
    response = client.run(agent, messages)
    print(response.messages[-1]["content"])