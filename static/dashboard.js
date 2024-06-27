document.addEventListener('DOMContentLoaded', () => {
    const dashboardItems = document.getElementById('dashboard-items');
    const goToChatButton = document.getElementById('go-to-chat');
    const goToToolsButton = document.getElementById('go-to-tools');

    goToChatButton.addEventListener('click', () => window.location.href = '/');
    goToToolsButton.addEventListener('click', () => window.location.href = '/tools');

    function loadDashboardItems() {
        const items = JSON.parse(localStorage.getItem('dashboardItems') || '[]');
        dashboardItems.innerHTML = '';
        items.forEach((item, index) => createDashboardItem(item, index));
    }

    function createDashboardItem(item, index) {
        const itemElement = document.createElement('div');
        itemElement.className = 'dashboard-item';
        itemElement.innerHTML = `
            <div class="dashboard-item-header">
                <h3>API Call: ${item.apiResponse.name || 'Unnamed API'}</h3>
                <div>
                    <button class="refresh-btn">Refresh</button>
                    <button class="edit-btn">Edit</button>
                    <button class="remove-btn">Remove</button>
                </div>
            </div>
            <div class="dashboard-item-content">
                <div class="api-response">
                    <h4>API Response:</h4>
                    <pre>${JSON.stringify(item.apiResponse, null, 2)}</pre>
                </div>
                <div class="component-container" id="component-${index}">
                    <h4>Component:</h4>
                    <!-- Component will be rendered here -->
                </div>
            </div>
            <div class="chat-window" style="display: none;">
                <textarea placeholder="Describe the component you want..."></textarea>
                <button class="generate-btn">Generate Component</button>
            </div>
        `;

        const refreshBtn = itemElement.querySelector('.refresh-btn');
        const editBtn = itemElement.querySelector('.edit-btn');
        const removeBtn = itemElement.querySelector('.remove-btn');
        const chatWindow = itemElement.querySelector('.chat-window');
        const generateBtn = itemElement.querySelector('.generate-btn');

        refreshBtn.addEventListener('click', () => refreshApiCall(item, index));
        editBtn.addEventListener('click', () => toggleChatWindow(chatWindow));
        removeBtn.addEventListener('click', () => removeDashboardItem(index));
        generateBtn.addEventListener('click', () => generateComponent(item, index));

        if (item.description) {
            generateComponent(item, index);
        }

        dashboardItems.appendChild(itemElement);
    }

    async function refreshApiCall(item, index) {
        // Implement API call refresh logic here
        console.log('Refreshing API call:', item.apiResponse.name);
    }

    function toggleChatWindow(chatWindow) {
        chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
    }

    function removeDashboardItem(index) {
        let items = JSON.parse(localStorage.getItem('dashboardItems') || '[]');
        items.splice(index, 1);
        localStorage.setItem('dashboardItems', JSON.stringify(items));
        loadDashboardItems();
    }

    async function generateComponent(item, index) {
        const chatWindow = document.querySelectorAll('.chat-window')[index];
        const description = chatWindow.querySelector('textarea').value.trim();
        if (!description) return;

        try {
            const response = await fetch('/generate_dashboard_component', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ query: description })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const component = await response.json();
            renderComponent(component, index);

            // Update local storage
            let items = JSON.parse(localStorage.getItem('dashboardItems') || '[]');
            items[index].description = description;
            localStorage.setItem('dashboardItems', JSON.stringify(items));

            toggleChatWindow(chatWindow);
        } catch (error) {
            console.error('Error generating component:', error);
            alert('Error generating component. Please try again.');
        }
    }

    function renderComponent(component, index) {
        const componentContainer = document.getElementById(`component-${index}`);
        componentContainer.innerHTML = `<h4>${component.title}</h4>`;

        if (component.type === 'chart') {
            Plotly.newPlot(`component-${index}`, component.data, component.layout);
        } else if (component.type === 'table') {
            renderTable(`component-${index}`, component.data);
        } else if (component.type === 'metric') {
            renderMetric(`component-${index}`, component.data);
        }
    }

    function renderTable(id, data) {
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>${Object.keys(data[0]).map(key => `<th>${key}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${data.map(row => `
                    <tr>${Object.values(row).map(value => `<td>${value}</td>`).join('')}</tr>
                `).join('')}
            </tbody>
        `;
        document.getElementById(id).appendChild(table);
    }

    function renderMetric(id, data) {
        const metricElement = document.createElement('div');
        metricElement.className = 'metric';
        metricElement.innerHTML = `
            <span class="metric-value">${data.value}</span>
            <span class="metric-label">${data.label}</span>
        `;
        document.getElementById(id).appendChild(metricElement);
    }

    loadDashboardItems();
});