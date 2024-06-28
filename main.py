import os
import asyncio
import logging
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from assistants import (
    create_assistant, create_thread, create_message, 
    run_assistant, get_run_status, get_assistant_response, submit_tool_outputs)

from tool_manager import ToolManager
from error_handlers import AppException, app_exception_handler, validation_exception_handler, general_exception_handler
from api_response_manager import api_response_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValueError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize ToolManager
tool_manager = ToolManager()

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    return templates.TemplateResponse("tools.html", {"request": request})




@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    logging.info(f"Received chat message: {message}")
    try:
        # Get or create assistant and thread
        assistant_id = request.session.get("assistant_id")
        thread_id = request.session.get("thread_id")
        
        logging.info(f"Assistant ID: {assistant_id}, Thread ID: {thread_id}")

        if not assistant_id:
            tools = tool_manager.get_available_tools()
            assistant = create_assistant(tools)
            request.session["assistant_id"] = assistant.id
            assistant_id = assistant.id
            logging.info(f"Created new assistant: {assistant_id}")
        
        if not thread_id:
            thread = create_thread()
            request.session["thread_id"] = thread.id
            thread_id = thread.id
            logging.info(f"Created new thread: {thread_id}")

        create_message(thread_id, message)
        logging.info(f"Created message in thread {thread_id}")

        async def event_generator():
            run = run_assistant(assistant_id, thread_id)
            logging.info(f"Started run: {run.id}")
            while True:
                run = get_run_status(thread_id, run.id)
                logging.info(f"Run status: {run.status}")
                if run.status == "completed":
                    response = get_assistant_response(thread_id)
                    logging.info(f"Assistant response: {response}")
                    yield f"data: {json.dumps({'type': 'assistant_message', 'content': response})}\n\n"
                    break
                elif run.status == "requires_action":
                    required_action = run.required_action
                    if required_action and required_action.type == "submit_tool_outputs":
                        tool_calls = required_action.submit_tool_outputs.tool_calls
                        tool_outputs = []
                        for tool_call in tool_calls:
                            tool_name = tool_call.function.name
                            tool = tool_manager.get_tool(tool_name)
                            if tool:
                                try:
                                    args = json.loads(tool_call.function.arguments)
                                    result = tool.execute(**args)
                                    tool_outputs.append({
                                        "tool_call_id": tool_call.id,
                                        "output": result
                                    })
                                    yield f"data: {json.dumps({'type': 'tool_output', 'name': tool_name, 'output': json.loads(result)})}\n\n"
                                except Exception as e:
                                    logging.error(f"Error executing tool {tool_name}: {str(e)}")
                                    error_output = json.dumps({"error": str(e)})
                                    tool_outputs.append({
                                        "tool_call_id": tool_call.id,
                                        "output": error_output
                                    })
                                    yield f"data: {json.dumps({'type': 'tool_output', 'name': tool_name, 'output': json.loads(error_output)})}\n\n"
                            else:
                                logging.error(f"Tool not found: {tool_name}")
                                error_output = json.dumps({"error": "Tool not found"})
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": error_output
                                })
                                yield f"data: {json.dumps({'type': 'tool_output', 'name': tool_name, 'output': json.loads(error_output)})}\n\n"
                        
                        submit_tool_outputs(thread_id, run.id, tool_outputs)
                        logging.info(f"Submitted tool outputs for run {run.id}")
                    
                    else:
                        logging.error(f"Unexpected required action: {required_action}")
                        yield f"data: {json.dumps({'type': 'error', 'content': 'An unexpected action is required. Please try again.'})}\n\n"
                        break
                elif run.status in ["failed", "expired", "cancelled"]:
                    error_message = f"Run failed with status: {run.status}"
                    if hasattr(run, 'last_error'):
                        error_message += f", Error: {run.last_error}"
                    logging.error(error_message)
                    yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"
                    break
                elif run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                else:
                    logging.error(f"Unexpected run status: {run.status}")
                    yield f"data: {json.dumps({'type': 'error', 'content': 'An unexpected error occurred. Please try again.'})}\n\n"
                    break


        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise AppException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during the chat process.")


@app.get("/api/tools")
async def get_tools():
    try:
        tools = tool_manager.get_all_tools()
        logger.info(f"Retrieved tools: {list(tools.keys())}")
        return JSONResponse(content={name: tool.__class__.__name__ for name, tool in tools.items()})
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools/{tool_name}")
async def get_tool(tool_name: str):
    tool_code = tool_manager.get_tool_code(tool_name)
    if tool_code is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return JSONResponse(content={"name": tool_name, "code": tool_code})

@app.put("/api/tools/{tool_name}")
async def update_tool(tool_name: str, code: str = Form(...)):
    try:
        tool_manager.update_tool(tool_name, code)
        return JSONResponse(content={"message": "Tool updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/tools")
async def create_tool(name: str = Form(...), code: str = Form(...)):
    try:
        tool_manager.create_tool(name, code)
        return JSONResponse(content={"message": "Tool created successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/response/{response_id}")
async def get_api_response(response_id: str):
    response = api_response_manager.get_response(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return JSONResponse(content=response)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/generate_dashboard_component")
async def generate_component(request: Request, query: str = Form(...)):
    try:
        tool = tool_manager.get_tool("dashboard_component_generator")
        if tool:
            result = tool.execute(query=query)
            # Return the raw component data
            return JSONResponse(content=json.loads(result))
        else:
            raise HTTPException(status_code=404, detail="Dashboard component generator tool not found")
    except Exception as e:
        logger.error(f"Error generating dashboard component: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh_api_call")
async def refresh_api_call(request: Request, tool_name: str = Form(...), args: str = Form(...)):
    try:
        tool = tool_manager.get_tool(tool_name)
        if tool:
            arguments = json.loads(args)
            result = tool.execute(**arguments)
            return JSONResponse(content=json.loads(result))
        else:
            raise HTTPException(status_code=404, detail="Tool not found")
    except Exception as e:
        logger.error(f"Error refreshing API call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)