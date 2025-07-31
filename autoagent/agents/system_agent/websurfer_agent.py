from autoagent.types import Agent
from autoagent.registry import register_agent
from autoagent.tools import click, page_down, page_up, history_back, history_forward, web_search, input_text, sleep, visit_url, get_page_markdown
from autoagent.tools.web_tools import with_env
from autoagent.environment.browser_env import BrowserEnv
import time
from constant import DOCKER_WORKPLACE_NAME, LOCAL_ROOT
@register_agent(name = "Web Surfer Agent", func_name="get_websurfer_agent")
def get_websurfer_agent(model: str = "gpt-4o", **kwargs):
    
    def handle_mm_func(tool_name, tool_args):
        return f"在执行了上一个操作 `{tool_name}({tool_args})` 后，当前页面的图像显示在下方。请根据图像、页面的当前状态以及之前的操作和观察结果来采取下一个操作。"
    def instructions(context_variables):
        web_env: BrowserEnv = context_variables.get("web_env", None)
        assert web_env is not None, "web_env is required"
        return \
f"""审查页面的当前状态和所有其他信息，以找到实现目标的最佳下一步操作。您的答案将被程序解释和执行，请确保遵循格式说明。

**重要提示：请用中文进行思考和分析，并在需要时使用中文表达您的推理过程。在<think>标签内也必须使用中文进行思考。**

请注意，如果您想分析YouTube视频、维基百科页面或其他包含媒体内容的页面，或者您只是想以更详细的方式分析页面的文本内容，您应该使用 `get_page_markdown` 工具将页面信息转换为markdown文本。在浏览网页时，如果您下载了任何文件，下载文件的路径将是 `{web_env.docker_workplace}/downloads`，您不能直接打开下载的文件，您应该转移回 `System Triage Agent`，让 `System Triage Agent` 转移到 `File Surfer Agent` 来打开下载的文件。

当您认为您已经完成了 `System Triage Agent` 要求您做的任务时，您应该使用 `transfer_back_to_triage_agent` 将对话转移回 `System Triage Agent`。您不应该停止尝试通过转移到 `System Triage Agent` 来解决用户的请求，直到任务完成。
"""
    
    tool_list = [click, page_down, page_up, history_back, history_forward, web_search, input_text, sleep, visit_url, get_page_markdown]
    return Agent(
        name="Web Surfer Agent", 
        model=model, 
        instructions=instructions,
        functions=tool_list,
        handle_mm_func=handle_mm_func,
        tool_choice = "required", 
        parallel_tool_calls = False
    )

"""
Note that when you need to download something, you should first know the url of the file, and then use the `visit_url` tool to download the file. For example, if you want to download paper from 'https://arxiv.org/abs/2310.13023', you should use `visit_url('url'='https://arxiv.org/pdf/2310.13023.pdf')`.
"""