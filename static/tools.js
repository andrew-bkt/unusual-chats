console.log('Tools.js loaded - version 1');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed for tools page');

    const toolList = document.getElementById('tool-list');
    const addNewToolButton = document.getElementById('add-new-tool');

    console.log('toolList:', toolList);
    console.log('addNewToolButton:', addNewToolButton);

    if (!toolList || !addNewToolButton) {
        console.error('One or more required elements are missing from the DOM');
        return;
    }

    function createToolItem(tool) {
        console.log('Creating tool item:', tool);
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';
        toolItem.innerHTML = `
            <span>${tool.name}</span>
            <button class="edit-button">Edit</button>
            <div class="edit-form" style="display:none;">
                <textarea class="code-input" rows="10" cols="50"></textarea>
                <button class="save-button">Save</button>
                <button class="cancel-button">Cancel</button>
            </div>
        `;

        const editButton = toolItem.querySelector('.edit-button');
        const editForm = toolItem.querySelector('.edit-form');
        const codeInput = toolItem.querySelector('.code-input');
        const saveButton = toolItem.querySelector('.save-button');
        const cancelButton = toolItem.querySelector('.cancel-button');

        editButton.addEventListener('click', async () => {
            console.log('Edit button clicked for tool:', tool.name);
            try {
                const response = await fetch(`/api/tools/${tool.name}`);
                const data = await response.json();
                codeInput.value = data.code;
                editForm.style.display = 'block';
                editButton.style.display = 'none';
            } catch (error) {
                console.error('Error fetching tool code:', error);
            }
        });

        saveButton.addEventListener('click', async () => {
            console.log('Save button clicked for tool:', tool.name);
            try {
                const response = await fetch(`/api/tools/${tool.name}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'code': codeInput.value
                    })
                });
                if (response.ok) {
                    editForm.style.display = 'none';
                    editButton.style.display = 'inline';
                    console.log('Tool updated successfully');
                } else {
                    console.error('Failed to update tool');
                }
            } catch (error) {
                console.error('Error updating tool:', error);
            }
        });

        cancelButton.addEventListener('click', () => {
            console.log('Cancel button clicked');
            editForm.style.display = 'none';
            editButton.style.display = 'inline';
        });

        return toolItem;
    }

    async function loadTools() {
        console.log('Loading tools...');
        try {
            const response = await fetch('/api/tools');
            const tools = await response.json();
            console.log('Loaded tools:', tools);
            toolList.innerHTML = '';
            Object.entries(tools).forEach(([name, className]) => {
                toolList.appendChild(createToolItem({name, className}));
            });
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    async function addNewTool() {
        console.log('Add new tool button clicked');
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
                    console.log('New tool created successfully');
                    loadTools();
                } else {
                    console.error('Failed to create new tool');
                }
            } catch (error) {
                console.error('Error creating new tool:', error);
            }
        }
    }

    loadTools();
    addNewToolButton.addEventListener('click', addNewTool);

    console.log('All event listeners set up for tools page');
});