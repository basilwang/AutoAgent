from pydantic import BaseModel, Field, validator, field_validator, ValidationInfo
from typing import List, Dict, Optional, Literal
import xml.etree.ElementTree as ET
import re

class KeyDescription(BaseModel):
    key: str
    description: str

class Tool(BaseModel):
    name: str
    description: str

class ToolSet(BaseModel):
    existing: List[Tool] = Field(default_factory=list)
    new: List[Tool] = Field(default_factory=list)

class GlobalVariable(BaseModel):
    key: str
    description: str
    value: str

class Agent(BaseModel):
    name: str
    description: str
    instructions: str
    tools: ToolSet
    agent_input: KeyDescription
    agent_output: KeyDescription

class AgentForm(BaseModel):
    system_input: str
    system_output: KeyDescription
    global_variables: Dict[str, GlobalVariable] = Field(default_factory=dict)
    agents: List[Agent]

    @field_validator('agents')
    def validate_single_agent_io(cls, v, info: ValidationInfo):
        """验证单代理系统的输入输出匹配"""
        if len(v) == 1:
            agent = v[0]
            system_output = info.data.get('system_output')
            if system_output and agent.agent_output.key != system_output.key:
                raise ValueError("Single agent system must have matching system and agent output keys")
        return v
    # def validate_global_ctx_instructions(cls, v, info: ValidationInfo):
    #     """验证全局变量和系统输入是否匹配"""

def clean_xml_content(xml_content: str) -> str:
    """清理XML内容，移除可能导致解析错误的字符"""
    print("DEBUG: 开始清理XML内容")
    print(f"原始内容长度: {len(xml_content)} 字符")
    
    # 移除可能的BOM标记
    xml_content = xml_content.strip()
    if xml_content.startswith('\ufeff'):
        xml_content = xml_content[1:]
        print("DEBUG: 移除了BOM标记")
    
    # 移除XML声明中的编码问题
    original_length = len(xml_content)
    xml_content = re.sub(r'<\?xml[^>]*encoding="[^"]*"[^>]*\?>', '', xml_content)
    if len(xml_content) != original_length:
        print("DEBUG: 移除了XML声明")
    
    # 确保XML内容被<agents>标签包围
    if not xml_content.strip().startswith('<agents>'):
        xml_content = f'<agents>{xml_content}</agents>'
        print("DEBUG: 添加了<agents>标签包围")
    
    # 移除多余的空格和换行符
    xml_content = re.sub(r'\s+', ' ', xml_content)
    print("DEBUG: 清理了多余的空格和换行符")
    
    print(f"清理后内容长度: {len(xml_content)} 字符")
    print(f"清理后内容前200字符: {xml_content[:200]}")
    
    return xml_content

class XMLParser:
    @staticmethod
    def parse_key_description(elem: ET.Element, tag_name: str) -> KeyDescription:
        node = elem.find(tag_name)
        if node is None:
            raise ValueError(f"Missing {tag_name}")
        key_elem = node.find('key')
        desc_elem = node.find('description')
        if key_elem is None or desc_elem is None:
            raise ValueError(f"Missing key or description in {tag_name}")
        return KeyDescription(
            key=key_elem.text.strip() if key_elem.text else '',
            description=desc_elem.text.strip() if desc_elem.text else ''
        )

    @staticmethod
    def parse_tools(agent_elem: ET.Element) -> ToolSet:
        tools = ToolSet()
        for tools_elem in agent_elem.findall('tools'):
            category = tools_elem.get('category')
            if category not in ('existing', 'new'):
                continue
            
            tool_list = []
            for tool_elem in tools_elem.findall('tool'):
                name_elem = tool_elem.find('name')
                desc_elem = tool_elem.find('description')
                if name_elem is not None and desc_elem is not None:
                    tool = Tool(
                        name=name_elem.text.strip() if name_elem.text else '',
                        description=desc_elem.text.strip() if desc_elem.text else ''
                    )
                    tool_list.append(tool)
            
            if category == 'existing':
                tools.existing = tool_list
            else:
                tools.new = tool_list
        
        return tools

    @staticmethod
    def parse_global_variables(root: ET.Element) -> Dict[str, GlobalVariable]:
        variables = {}
        global_vars = root.find('global_variables')
        if global_vars is not None:
            for var in global_vars.findall('variable'):
                key_elem = var.find('key')
                desc_elem = var.find('description')
                value_elem = var.find('value')
                if key_elem is not None and desc_elem is not None and value_elem is not None:
                    key = key_elem.text.strip() if key_elem.text else ''
                    variables[key] = GlobalVariable(
                        key=key,
                        description=desc_elem.text.strip() if desc_elem.text else '',
                        value=value_elem.text.strip() if value_elem.text else ''
                    )
        return variables

    @classmethod
    def parse_agent(cls, agent_elem: ET.Element) -> Agent:
        name_elem = agent_elem.find('name')
        desc_elem = agent_elem.find('description')
        instructions_elem = agent_elem.find('instructions')
        
        if name_elem is None or desc_elem is None or instructions_elem is None:
            raise ValueError("Missing required elements in agent definition")
        
        return Agent(
            name=name_elem.text.strip() if name_elem.text else '',
            description=desc_elem.text.strip() if desc_elem.text else '',
            instructions=instructions_elem.text.strip() if instructions_elem.text else '',
            tools=cls.parse_tools(agent_elem),
            agent_input=cls.parse_key_description(agent_elem, 'agent_input'),
            agent_output=cls.parse_key_description(agent_elem, 'agent_output')
        )

    @classmethod
    def parse_xml(cls, xml_content: str) -> AgentForm:
        # 清理XML内容
        xml_content = clean_xml_content(xml_content)
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            # 尝试修复常见的XML格式问题
            xml_content = re.sub(r'&(?![a-zA-Z]+;)', '&amp;', xml_content)
            root = ET.fromstring(xml_content)
        
        system_input_elem = root.find('system_input')
        if system_input_elem is None:
            raise ValueError("Missing system_input element")
        
        return AgentForm(
            system_input=system_input_elem.text.strip() if system_input_elem.text else '',
            system_output=cls.parse_key_description(root, 'system_output'),
            global_variables=cls.parse_global_variables(root),
            agents=[cls.parse_agent(agent_elem) for agent_elem in root.findall('agent')]
        )

def parse_agent_form(xml_content: str) -> Optional[AgentForm]:
    """
    读取并解析agent form XML文件
    
    Args:
        xml_content: XML文件内容
    
    Returns:
        解析后的AgentForm对象，如果解析失败返回None
    """
    print("=" * 60)
    print("DEBUG: 开始解析XML内容")
    print("=" * 60)
    print(f"XML内容长度: {len(xml_content)} 字符")
    print(f"XML内容前200字符: {xml_content[:200]}")
    print("=" * 60)
    
    try:
        result = XMLParser.parse_xml(xml_content)
        print("DEBUG: XML解析成功")
        return result
    
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        print(f"XML content: {xml_content[:500]}...")  # 打印前500个字符用于调试
        print(f"DEBUG: XML解析错误位置 - 行: {e.position[0]}, 列: {e.position[1]}")
        print(f"DEBUG: 错误代码: {e.code}")
        print(f"DEBUG: 错误消息: {e.msg}")
        
        # 尝试定位错误位置
        lines = xml_content.split('\n')
        if e.position[0] <= len(lines):
            print(f"DEBUG: 错误行内容: {lines[e.position[0]-1]}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"DEBUG: 异常类型: {type(e).__name__}")
        print(f"DEBUG: 异常详情: {str(e)}")
        return None
