"""
Core workflow engine.
"""

import logging
import datetime
import json
import os
from typing import Dict, List, Any, Optional, Union
from .models import (
    Workflow, WorkflowExecution, Component, Connection,
    AgentComponent, PluginComponent, DataSourceComponent,
    InputComponent, OutputComponent, ComponentType
)
from .executor import WorkflowExecutionManager

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Core workflow engine."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.workflows = {}
        self.execution_manager = WorkflowExecutionManager()
        self.storage_dir = storage_dir
        
        # Create storage directory if it doesn't exist
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        # Load workflows from storage if available
        if storage_dir:
            self._load_workflows()
    
    def _load_workflows(self):
        """Load workflows from storage."""
        if not self.storage_dir:
            return
        
        workflows_dir = os.path.join(self.storage_dir, "workflows")
        if not os.path.exists(workflows_dir):
            os.makedirs(workflows_dir)
            return
        
        for filename in os.listdir(workflows_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(workflows_dir, filename), "r") as f:
                        workflow_data = json.load(f)
                        workflow = Workflow(**workflow_data)
                        self.workflows[workflow.id] = workflow
                except Exception as e:
                    logger.error(f"Error loading workflow {filename}: {e}")
    
    def _save_workflow(self, workflow: Workflow):
        """Save a workflow to storage."""
        if not self.storage_dir:
            return
        
        workflows_dir = os.path.join(self.storage_dir, "workflows")
        if not os.path.exists(workflows_dir):
            os.makedirs(workflows_dir)
        
        try:
            with open(os.path.join(workflows_dir, f"{workflow.id}.json"), "w") as f:
                f.write(workflow.json(indent=2))
        except Exception as e:
            logger.error(f"Error saving workflow {workflow.id}: {e}")
    
    def create_workflow(self, name: str, description: Optional[str] = None) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(
            name=name,
            description=description,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )
        self.workflows[workflow.id] = workflow
        self._save_workflow(workflow)
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        return list(self.workflows.values())
    
    def update_workflow(self, workflow_id: str, **kwargs) -> Optional[Workflow]:
        """Update a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Update workflow fields
        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        # Update updated_at timestamp
        workflow.updated_at = datetime.datetime.now().isoformat()
        
        # Save the workflow
        self._save_workflow(workflow)
        
        return workflow
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id not in self.workflows:
            return False
        
        # Remove from memory
        del self.workflows[workflow_id]
        
        # Remove from storage
        if self.storage_dir:
            workflow_file = os.path.join(self.storage_dir, "workflows", f"{workflow_id}.json")
            if os.path.exists(workflow_file):
                os.remove(workflow_file)
        
        return True
    
    def add_component(self, workflow_id: str, component: Union[Component, Dict[str, Any]]) -> Optional[Component]:
        """Add a component to a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Convert dict to Component if needed
        if isinstance(component, dict):
            component_type = component.get("type")
            if component_type == ComponentType.AGENT:
                component = AgentComponent(**component)
            elif component_type == ComponentType.PLUGIN:
                component = PluginComponent(**component)
            elif component_type == ComponentType.DATA_SOURCE:
                component = DataSourceComponent(**component)
            elif component_type == ComponentType.INPUT:
                component = InputComponent(**component)
            elif component_type == ComponentType.OUTPUT:
                component = OutputComponent(**component)
            else:
                component = Component(**component)
        
        # Add the component to the workflow
        workflow.components.append(component)
        
        # Update the workflow
        workflow.updated_at = datetime.datetime.now().isoformat()
        self._save_workflow(workflow)
        
        return component
    
    def update_component(self, workflow_id: str, component_id: str, **kwargs) -> Optional[Component]:
        """Update a component in a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Find the component
        component = None
        for c in workflow.components:
            if c.id == component_id:
                component = c
                break
        
        if not component:
            return None
        
        # Update component fields
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
        
        # Update the workflow
        workflow.updated_at = datetime.datetime.now().isoformat()
        self._save_workflow(workflow)
        
        return component
    
    def delete_component(self, workflow_id: str, component_id: str) -> bool:
        """Delete a component from a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        # Find the component
        component_index = None
        for i, c in enumerate(workflow.components):
            if c.id == component_id:
                component_index = i
                break
        
        if component_index is None:
            return False
        
        # Remove the component
        workflow.components.pop(component_index)
        
        # Remove any connections involving the component
        workflow.connections = [
            c for c in workflow.connections
            if c.source_id != component_id and c.target_id != component_id
        ]
        
        # Update the workflow
        workflow.updated_at = datetime.datetime.now().isoformat()
        self._save_workflow(workflow)
        
        return True
    
    def add_connection(self, workflow_id: str, connection: Union[Connection, Dict[str, Any]]) -> Optional[Connection]:
        """Add a connection to a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Convert dict to Connection if needed
        if isinstance(connection, dict):
            connection = Connection(**connection)
        
        # Validate the connection
        source_exists = any(c.id == connection.source_id for c in workflow.components)
        target_exists = any(c.id == connection.target_id for c in workflow.components)
        
        if not source_exists or not target_exists:
            logger.error(f"Invalid connection: source or target component does not exist")
            return None
        
        # Add the connection to the workflow
        workflow.connections.append(connection)
        
        # Update the workflow
        workflow.updated_at = datetime.datetime.now().isoformat()
        self._save_workflow(workflow)
        
        return connection
    
    def delete_connection(self, workflow_id: str, connection_id: str) -> bool:
        """Delete a connection from a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        # Find the connection
        connection_index = None
        for i, c in enumerate(workflow.connections):
            if c.id == connection_id:
                connection_index = i
                break
        
        if connection_index is None:
            return False
        
        # Remove the connection
        workflow.connections.pop(connection_index)
        
        # Update the workflow
        workflow.updated_at = datetime.datetime.now().isoformat()
        self._save_workflow(workflow)
        
        return True
    
    async def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Optional[WorkflowExecution]:
        """Execute a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Execute the workflow
        execution = await self.execution_manager.execute_workflow(workflow, inputs, context)
        
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID."""
        return self.execution_manager.get_execution(execution_id)
    
    def list_executions(self, workflow_id: Optional[str] = None) -> List[WorkflowExecution]:
        """List workflow executions, optionally filtered by workflow ID."""
        return self.execution_manager.list_executions(workflow_id)
