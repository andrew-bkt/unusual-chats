document.addEventListener('DOMContentLoaded', () => {
    const toolList = document.getElementById('tool-list');
    const toolEditor = document.getElementById('tool-editor');
    const addNewToolButton = document.getElementById('add-new-tool');
    const goToChatButton = document.getElementById('go-to-chat');

    function createToolItem(tool) {
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';
        toolItem.textContent = tool.name;
        toolItem.addEventListener('click', () => loadToolCode(tool.name));
        return toolItem;
    }

    async function loadTools() {
        try {
            const response = await fetch('/api/tools');
            const tools = await response.json();
            toolList.innerHTML = '';
            Object.entries(tools).forEach(([name, className]) => {
                toolList.appendChild(createToolItem({name, className}));
            });
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    async function loadToolCode(toolName) {
        try {
            const response = await fetch(`/api/tools/${toolName}`);
            const data = await response.json();
            displayToolEditor(toolName, data.code);
        } catch (error) {
            console.error('Error fetching tool code:', error);
        }
    }

    function displayToolEditor(toolName, code) {
        toolEditor.innerHTML = `
            <h3>${toolName}</h3>
            <textarea class="code-input" rows="10" cols="50">${code}</textarea>
            <div>
                <button class="save-button">Save</button>
                <button class="cancel-button">Cancel</button>
            </div>
        `;

        const saveButton = toolEditor.querySelector('.save-button');
        const cancelButton = toolEditor.querySelector('.cancel-button');
        const codeInput = toolEditor.querySelector('.code-input');

        saveButton.addEventListener('click', () => saveToolCode(toolName, codeInput.value));
        cancelButton.addEventListener('click', () => toolEditor.innerHTML = '');
    }

    async function saveToolCode(toolName, code) {
        try {
            const response = await fetch(`/api/tools/${toolName}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'code': code
                })
            });
            if (response.ok) {
                alert('Tool updated successfully');
                loadTools();
            } else {
                alert('Failed to update tool');
            }
        } catch (error) {
            console.error('Error updating tool:', error);
            alert('Error updating tool');
        }
    }

    async function addNewTool() {
        const name = prompt('Enter the name for the new tool:');
        if (name) {
            const code = `from tool_plugins.base_tool import BaseTool

class ${name}(BaseTool):
    def execute(self, *args, **kwargs):
        # Tool logic here
        pass

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                # Define properties here
            },
            "required": []
        }

    def get_description(self):
        return "Description of ${name}"`;

            try {
                const response = await fetch('/api/tools', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'name': name,
                        'code': code
                    })
                });
                if (response.ok) {
                    alert('New tool created successfully');
                    loadTools();
                } else {
                    alert('Failed to create new tool');
                }
            } catch (error) {
                console.error('Error creating new tool:', error);
                alert('Error creating new tool');
            }
        }
    }

    loadTools();
    addNewToolButton.addEventListener('click', addNewTool);
    goToChatButton.addEventListener('click', () => window.location.href = '/');
});