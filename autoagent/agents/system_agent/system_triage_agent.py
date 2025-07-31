from .filesurfer_agent import get_filesurfer_agent
from .programming_agent import get_coding_agent
from .websurfer_agent import get_websurfer_agent
from autoagent.registry import register_agent, register_tool
from autoagent.types import Agent, Result
from autoagent.tools.inner import case_resolved, case_not_resolved

@register_agent(name = "System Triage Agent", func_name="get_system_triage_agent")
def get_system_triage_agent(model: str, **kwargs):
    """
    This is the `System Triage Agent`, it can help the user to determine which agent is best suited to handle the user's request under the current context, and transfer the conversation to that agent.
    
    Args:
        model: The model to use for the agent.
        **kwargs: Additional keyword arguments, `file_env`, `web_env` and `code_env` are required.
    """
    filesurfer_agent = get_filesurfer_agent(model)
    websurfer_agent = get_websurfer_agent(model)
    coding_agent = get_coding_agent(model)
    instructions = \
f"""您是一个有用的助手，可以帮助用户处理他们的请求。
根据解决用户任务的状态，您的职责是确定哪个代理最适合在当前上下文中处理用户的请求，并将对话转移到该代理。您不应该停止尝试通过转移到另一个代理来解决用户的请求，直到任务完成。

**重要提示：请用中文进行思考和分析，并在需要时使用中文表达您的推理过程。**

您可以将对话转移到以下三个代理：
1. 使用 `transfer_to_filesurfer_agent` 转移到 {filesurfer_agent.name}，它可以帮助您打开任何类型的本地文件并浏览其内容。
2. 使用 `transfer_to_websurfer_agent` 转移到 {websurfer_agent.name}，它可以帮助您打开任何网站并浏览其内容。
3. 使用 `transfer_to_coding_agent` 转移到 {coding_agent.name}，它可以帮助您编写代码来解决用户的请求，特别是一些复杂的任务。
"""
    tool_choice = "required" 
    tools = [case_resolved, case_not_resolved] if tool_choice == "required" else []
    system_triage_agent = Agent(
        name="System Triage Agent",
        model=model, 
        instructions=instructions,
        functions=tools,
        tool_choice = tool_choice, 
        parallel_tool_calls = False,
    )
    def transfer_to_filesurfer_agent(sub_task_description: str):
        """
        Args:
            sub_task_description: The detailed description of the sub-task that the `System Triage Agent` will ask the `File Surfer Agent` to do.
        """
        return Result(value=sub_task_description, agent=filesurfer_agent)
    def transfer_to_websurfer_agent(sub_task_description: str):
        return Result(value=sub_task_description, agent=websurfer_agent)
    def transfer_to_coding_agent(sub_task_description: str):
        return Result(value=sub_task_description, agent=coding_agent)
    def transfer_back_to_triage_agent(task_status: str):
        """
        Args:
            task_status: The detailed description of the task status after a sub-agent has finished its sub-task. A sub-agent can use this tool to transfer the conversation back to the `System Triage Agent` only when it has finished its sub-task.
        """
        return Result(value=task_status, agent=system_triage_agent)
    system_triage_agent.agent_teams = {
        filesurfer_agent.name: transfer_to_filesurfer_agent,
        websurfer_agent.name: transfer_to_websurfer_agent,
        coding_agent.name: transfer_to_coding_agent
    }
    system_triage_agent.functions.extend([transfer_to_filesurfer_agent, transfer_to_websurfer_agent, transfer_to_coding_agent])
    filesurfer_agent.functions.append(transfer_back_to_triage_agent)
    websurfer_agent.functions.append(transfer_back_to_triage_agent)
    coding_agent.functions.append(transfer_back_to_triage_agent)
    return system_triage_agent

    