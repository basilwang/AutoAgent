from autoagent.types import Agent
from autoagent.registry import register_agent
from autoagent.tools import open_local_file, page_up_markdown, page_down_markdown, find_on_page_ctrl_f, find_next, visual_question_answering
from autoagent.tools.file_surfer_tool import with_env
from autoagent.environment.markdown_browser import RequestsMarkdownBrowser
import time
from inspect import signature
from constant import LOCAL_ROOT, DOCKER_WORKPLACE_NAME
@register_agent(name = "File Surfer Agent", func_name="get_filesurfer_agent")
def get_filesurfer_agent(model: str = "gpt-4o", **kwargs):
    
    def handle_mm_func(tool_name, tool_args):
        return f"在使用工具 `{tool_name}({tool_args})` 后，我已经打开了我想查看的图像，并根据图像准备了一个问题。请根据图像回答这个问题。"
    def instructions(context_variables):
        file_env: RequestsMarkdownBrowser = context_variables.get("file_env", None)
        assert file_env is not None, "file_env is required"
        return \
f"""
您是一个可以处理本地文件的文件浏览代理。

您只能访问文件夹 `{file_env.docker_workplace}` 中的文件，当您想要打开文件时，您应该使用从根目录开始的绝对路径，如 `{file_env.docker_workplace}/...`。

**重要提示：请用中文进行思考和分析，并在需要时使用中文表达您的推理过程。在<think>标签内也必须使用中文进行思考。**

请注意，`open_local_file` 可以将文件读取为markdown文本并询问相关问题。`open_local_file` 可以处理以下文件扩展名：[".html", ".htm", ".xlsx", ".pptx", ".wav", ".mp3", ".flac", ".pdf", ".docx"]，以及所有其他类型的文本文件。

但是它不能处理图像，您应该使用 `visual_question_answering` 来查看图像。

如果转换的markdown文本超过1页，您可以使用 `page_up`、`page_down`、`find_on_page_ctrl_f`、`find_next` 来浏览页面。

当您认为您已经完成了 `System Triage Agent` 要求您做的任务时，您应该使用 `transfer_back_to_triage_agent` 将对话转移回 `System Triage Agent`。

如果您无法打开文件或遇到其他问题，您也应该使用 `transfer_back_to_triage_agent` 将对话转移回 `System Triage Agent`，让其他代理（如 `Coding Agent`）尝试通过其他方式解决问题。
"""
    tool_list = [open_local_file, page_up_markdown, page_down_markdown, find_on_page_ctrl_f, find_next, visual_question_answering]
    return Agent(
        name="File Surfer Agent",
        model=model, 
        instructions=instructions,
        functions=tool_list,
        handle_mm_func=handle_mm_func,
        tool_choice = "required", 
        parallel_tool_calls = False
    )

