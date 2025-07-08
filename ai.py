# %%
from config import Config
import os

if Config.LOCAL_TEST:
    from dotenv import load_dotenv
    load_dotenv()

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
LLMAAS_OPENAI_API_KEY = os.environ.get("LLMAAS_OPENAI_API_KEY")

# %%
from langgraph.graph import MessagesState
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import random

# Parse LLM output
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts.chat import HumanMessagePromptTemplate
import json

#Logging
import customLogging

#For Throttling
import time

#For Statistics
import ai_counter

#Custom imports
from config import Config
from prompt_template import SECTION_TEMPLATES, messagePromptInstruction

# Initialize global tracker
usage_tracker = ai_counter.UsageTracker()

logger = customLogging.safe_logger_setup()

# Pydantic models to represent the data structure
class Field(BaseModel):
    name: str
    value: str
    type: str

class Section(BaseModel):
    label: str
    type: str
    fields: List[Field]

class ProfileResponse(BaseModel):
    """Complete profile response containing all requested sections"""
    InfoSectionList: List[Section]


def create_section_data(sections: List[str]) -> List[Dict[str, Any]]:
    """
    Generate section data based on requested section types
    Args:
        sections: List of section types to include
                 Options: ['main_particulars', 'education', 'career', 'appointments', 'remarks']
    Returns:
        List of section dictionaries
    """

    # Section templates with predefined data
    section_templates = SECTION_TEMPLATES

    # Build the result list based on requested sections
    result = []
    for section_name in sections:
        if section_name in section_templates:
            result.append(section_templates[section_name])
        else:
            available_sections = list(section_templates.keys())
            logger.info(f"Warning: Section '{section_name}' not found. Available sections: {available_sections}")

    return result

def create_sections_as_pydantic(sections: List[str]) -> List[Section]:
    """Create sections as Pydantic model objects"""

    section_dicts = create_section_data(sections)
    return [Section(**section_dict) for section_dict in section_dicts]

# Convert to JSON string for human message
def sections_to_json(sections: List[str]) -> str:
    """Convert sections to JSON string for human message"""
    section_data = create_section_data(sections)
    return json.dumps(section_data, indent=2)

def embed_in_transaction_format(sections_json_str: str, transaction_id: str) -> str:
    """Embed existing sections JSON string into transaction format"""
    # Parse the existing JSON string back to object
    clean_json_str = sections_json_str.replace('```json\n', '').replace('\n```', '')
    sections_data = json.loads(clean_json_str)

    wrapper = {
        "TransactionId": transaction_id,
        "InfoSectionList": sections_data
    }

    return wrapper


# %%
# Create the Tavily search tool
def initialize_tavily_tools(max_results=Config.TAVILY_MAXSEARCH, search_topic=Config.TAVILY_SEARCHTOPIC):
    """
    Initialize Tavily search and extract tools
    
    Args:
        max_results (int): Maximum search results to return
        search_topic (str): Topic for search filtering
    
    Returns:
        tuple: (tavily_search_tool, tavily_extract_tool)
    """
    # Initialize Tavily Search Tool
    tavily_search_tool = TavilySearch(
        max_results=max_results or 5,  # Default to 5 if not provided
        topic=search_topic or "general",  # Default topic
        summarize=True,  # Enable summarization
    )
    
    # Initialize Tavily Extract Tool
    tavily_extract_tool = TavilyExtract()
    
    return tavily_search_tool, tavily_extract_tool

def initialize_chat_model(api_key=LLMAAS_OPENAI_API_KEY, api_base=Config.LLMAAS_BASEURL, model_name=Config.LLMAAS_MODELNAME, tools=None, temperature=Config.LLM_TEMPERATURE):
    """
    Initialize ChatOpenAI model with optional tools binding
    
    Args:
        api_key (str): OpenAI API key
        api_base (str): Base URL for API
        model_name (str): Model name to use
        tools (list): List of tools to bind to model
    
    Returns:
        ChatOpenAI: Configured chat model
    """
    model = ChatOpenAI(
        api_key=api_key,
        openai_api_base=api_base,
        model=model_name or "gpt-4o-mini-prd-gcc2-lb",
        temperature=0 or temperature,
    )
    
    if tools:
        model = model.bind_tools(tools)
    
    return model

#Create Assistant Node
def create_assistant_node(model_with_tools, system_message=SystemMessage(content=Config.SYSTEM_CONTENT),throttleSec=Config.THROTTLESPEED,model_name="gpt4omini"):
    """
    Create assistant node function for the graph
    
    Args:
        model_with_tools: Chat model with tools bound
        system_message: Optional system message to prepend
        enable_streaming: Whether to enable streaming output
    Returns:
        function: Assistant node function
    """
    def assistant(state: MessagesState):
        messages = state['messages']
        
        # Log incoming request with timestamp
        logger.info(f"Assistant node called with {len(messages)} messages")
        if messages:
            safe_message = customLogging.safe_log_text(messages[-1].content)
            logger.info(f"Last message: {safe_message}")
        else:
            logger.info("Last message: No messages")

        # Count input tokens
        input_tokens =ai_counter.count_messages_tokens(messages, model_name)

        # Add system message tokens if present
        if system_message:
            input_tokens += ai_counter.count_tokens(system_message.content, model_name)

        if len(messages) > 2:
            logger.info(f"Sleeping {throttleSec} seconds before invoking model")
            time.sleep(throttleSec)

        logger.info("Invoking model (non-streaming)")

        # Increment request counter
        usage_tracker.increment_request()

        response = model_with_tools.invoke(messages)

        # Count output tokens
        output_tokens = ai_counter.count_tokens(response.content, model_name)

        # Update token counters
        usage_tracker.add_tokens(input_tokens, output_tokens)

        # Log usage statistics
        current_stats = usage_tracker.get_stats()
        logger.info(f"Current request - Input tokens: {input_tokens}, Output tokens: {output_tokens}")
        logger.info(f"Total usage - Requests: {current_stats['total_requests']}, "
                   f"Input tokens: {current_stats['total_input_tokens']}, "
                   f"Output tokens: {current_stats['total_output_tokens']}, "
                   f"Total tokens: {current_stats['total_tokens']}")

        logger.info(f"Model response received: {response.content[:500]}......")
        return {"messages": [response]}
        # return {"messages": [model_with_tools.invoke(messages)]}
    
    return assistant



# %%
# build graph

from datetime import datetime

def build_graph(assistant_node, tavily_search_tool, use_memory=True):

    logger.info("Building graph...")

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node('assistant', assistant_node)
    graph_builder.add_node('tools', ToolNode(tavily_search_tool))
    graph_builder.set_entry_point('assistant')
    graph_builder.add_conditional_edges(
        'assistant',
        tools_condition
    )
    graph_builder.add_edge('tools','assistant')
    graph_builder.set_finish_point('assistant')

    #add memory
    memory = MemorySaver() if use_memory else None
    graph = graph_builder.compile(checkpointer=memory)
    logger.info("Graph compilation completed")

    return graph


# %%


def process_messages(name=None, countryName=None, designation="", transaction_id="", system_content_template=Config.SYSTEM_CONTENT,
                    human_message_template=Config.HUMAN_MESSAGE_TEMPLATE, sectionNameList=["main_particulars","education","career","appointments","reference"], 
                    graph=None):

    sectionInstructions = [messagePromptInstruction(sectionName) for sectionName in sectionNameList]
    output_format = sections_to_json(sectionName for sectionName in sectionNameList)
    logger.info(f"Output format of the human message: {output_format}")

    formatted_human_message_template = human_message_template.format(
        name=name,
        countryName=countryName,
        designation=designation,
        sectionInstructions=sectionInstructions,
        output_format=output_format
    )
    
    # Create the message objects

    human_message = HumanMessage(content=formatted_human_message_template)
    logger.info(f"Generated full human message: {human_message}")

    if transaction_id == "":
        logger.info("No transaction id is given.  To generate a transaction id. ")
        thread_id = str(random.randint(1, 1000000))
        logger.info(f"Generated Transaction ID is {transaction_id}")
    else:
        logger.info(f"Transaction ID is {transaction_id}")
        thread_id = transaction_id

    thread = {"configurable": {"thread_id": thread_id}}

    # Check if this is a new thread and initialize if needed
    try:
        state = graph.get_state(thread)
        if not state.values.get('messages'):
            # New thread - initialize with system message
            logger.info(f"Initializing new thread {thread_id} with system message")
            graph.update_state(thread, {"messages": [SystemMessage(content=system_content_template)]})
        else:
            logger.info(f"Thread {thread_id} already has {len(state.values['messages'])} messages")
    except Exception as e:
        # Thread doesn't exist or error occurred - initialize with system message
        logger.info(f"Thread {thread_id} doesn't exist or error occurred: {e}")
        logger.info(f"Creating and initializing thread {thread_id}")
        graph.update_state(thread, {"messages": [SystemMessage(content=Config.SYSTEM_CONTENT)]})

    logger.info(f"Invoke graph with human message and threadID {thread_id}")

    

    messages = graph.invoke({"messages": [human_message]}, thread)
    logger.info("=== Full list of messages ===")
    # logger.info(messages['messages'][-1].pretty_print())
    for m in messages['messages']:
        logger.info(m)

    formatMsg = embed_in_transaction_format(messages['messages'][-1].content, thread_id)
    return formatMsg, thread_id




# %%
# thread = {"configurable": {"thread_id" : str(random.randint(1, 100))}}
# messages = graph.invoke({"messages" : [system_message, human_message]}, thread)
# for m in messages['messages']:
#     m.pretty_print()

def create_graph():

    logger.info("Initialize Tavily Tool")
    # 1. Initialize tools
    tavily_search_tool, tavily_extract_tool = initialize_tavily_tools(
        max_results=Config.TAVILY_MAXSEARCH,
        search_topic=Config.TAVILY_SEARCHTOPIC
    )
    
    # 2. Initialize model
    logger.info("Initialize Chat Model")
    model_with_tools = initialize_chat_model(
        api_key=LLMAAS_OPENAI_API_KEY,
        tools=[tavily_search_tool]
    )
    # model_with_tools = initialize_chat_model(
    #     api_key=OPENAI_API_KEY,
    #     tools=[tavily_search_tool],
    #     model_name="gpt-4o-mini"
    # )
    
    # 3. Create system message
    logger.info("Initialize System Message")
    system_message = SystemMessage(content=Config.SYSTEM_CONTENT)
    
    # 4. Create assistant node
    logger.info("Create assistant node")
    assistant_node = create_assistant_node(model_with_tools, system_message)
    
    # 5. Build graph
    logger.info("Build graph")
    graph= build_graph(assistant_node, [tavily_search_tool])

    return graph

