import os
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_assistant(tools):
    logger.info(f"Creating assistant with tools: {tools}")
    assistant = client.beta.assistants.create(
        name="Chat Assistant",
        instructions="You are a helpful assistant specializing in options trading data. Use the provided tools to fetch and analyze options data when requested.",
        tools=tools,
        model="gpt-4-1106-preview"
    )
    logger.info(f"Created assistant with ID: {assistant.id}")
    return assistant

def create_thread():
    thread = client.beta.threads.create()
    logger.info(f"Created thread with ID: {thread.id}")
    return thread

def create_message(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    logger.info(f"Created message in thread {thread_id}")
    return message

def run_assistant(assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    logger.info(f"Started run {run.id} for assistant {assistant_id} in thread {thread_id}")
    return run


def submit_tool_outputs(thread_id, run_id, tool_outputs):
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )

def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    logger.info(f"Run {run_id} status: {run.status}")
    return run  # Return the full run object instead of just the status


def get_assistant_response(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    logger.info(f"Retrieved messages for thread {thread_id}")
    return messages.data[0].content[0].text.value