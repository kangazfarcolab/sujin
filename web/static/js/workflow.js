/**
 * Main workflow UI entry point
 * Initializes and coordinates all workflow modules
 */

// Import modules
import WorkflowManager from './workflow/workflow-manager.js';
import ComponentManager from './workflow/component-manager.js';
import CanvasManager from './workflow/canvas-manager.js';
import ConnectionManager from './workflow/connection-manager.js';
import ExecutionManager from './workflow/execution-manager.js';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize managers
        const workflowManager = new WorkflowManager();
        const componentManager = new ComponentManager();
        const canvasManager = new CanvasManager();
        const connectionManager = new ConnectionManager(canvasManager);
        const executionManager = new ExecutionManager();
        
        // Initialize modules
        await workflowManager.initialize();
        await componentManager.initialize();
        await canvasManager.initialize();
        await connectionManager.initialize();
        await executionManager.initialize();
        
        console.log('Workflow UI initialized successfully');
    } catch (error) {
        console.error('Error initializing workflow UI:', error);
    }
});
