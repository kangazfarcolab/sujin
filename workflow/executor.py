"""
Workflow execution logic.
"""

import logging
import asyncio
import datetime
from typing import Dict, List, Any, Optional, Set
from .models import Workflow, WorkflowExecution, Component, Connection
from .components import registry, ComponentExecutor

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executor for workflows."""
    
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.execution = WorkflowExecution(workflow_id=workflow.id)
        self.component_executors = {}
        self.component_results = {}
        self.component_errors = {}
        self.component_dependencies = {}
        self.component_dependents = {}
        self.ready_components = set()
        self.completed_components = set()
        self.failed_components = set()
    
    def _initialize(self):
        """Initialize the workflow execution."""
        # Create component executors
        for component in self.workflow.components:
            component_class = registry.get(component.type)
            if component_class:
                self.component_executors[component.id] = component_class(component)
            else:
                logger.error(f"Unknown component type: {component.type}")
                self.component_errors[component.id] = f"Unknown component type: {component.type}"
        
        # Build dependency graph
        for connection in self.workflow.connections:
            source_id = connection.source_id
            target_id = connection.target_id
            
            # Add target as dependent of source
            if source_id not in self.component_dependents:
                self.component_dependents[source_id] = set()
            self.component_dependents[source_id].add(target_id)
            
            # Add source as dependency of target
            if target_id not in self.component_dependencies:
                self.component_dependencies[target_id] = set()
            self.component_dependencies[target_id].add(source_id)
        
        # Find components with no dependencies (ready to execute)
        for component in self.workflow.components:
            if component.id not in self.component_dependencies:
                self.ready_components.add(component.id)
    
    async def execute(self, inputs: Dict[str, Any] = None, context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute the workflow with the given inputs and context."""
        if inputs is None:
            inputs = {}
        if context is None:
            context = {}
        
        # Initialize the workflow execution
        self._initialize()
        
        # Set execution start time
        self.execution.start_time = datetime.datetime.now().isoformat()
        self.execution.status = "running"
        
        # Add inputs to component results for input components
        for component in self.workflow.components:
            if component.type == "input":
                self.component_results[component.id] = inputs
                self.completed_components.add(component.id)
                
                # Update ready components
                if component.id in self.component_dependents:
                    for dependent_id in self.component_dependents[component.id]:
                        # Check if all dependencies of the dependent are completed
                        if dependent_id in self.component_dependencies:
                            dependencies = self.component_dependencies[dependent_id]
                            if all(dep_id in self.completed_components for dep_id in dependencies):
                                self.ready_components.add(dependent_id)
        
        # Execute components until all are completed or failed
        while self.ready_components:
            # Get a component to execute
            component_id = next(iter(self.ready_components))
            self.ready_components.remove(component_id)
            
            # Skip if already completed or failed
            if component_id in self.completed_components or component_id in self.failed_components:
                continue
            
            # Get the component executor
            executor = self.component_executors.get(component_id)
            if not executor:
                logger.error(f"No executor for component: {component_id}")
                self.component_errors[component_id] = "No executor for component"
                self.failed_components.add(component_id)
                continue
            
            # Get inputs for the component
            component_inputs = {}
            if component_id in self.component_dependencies:
                for dependency_id in self.component_dependencies[component_id]:
                    if dependency_id in self.component_results:
                        # Merge the dependency results into the component inputs
                        component_inputs.update(self.component_results[dependency_id])
            
            # Execute the component
            try:
                result = await executor.execute(component_inputs, context)
                self.component_results[component_id] = result
                self.completed_components.add(component_id)
                
                # Log the execution
                self.execution.logs.append({
                    "component_id": component_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "completed",
                    "result": result
                })
                
                # Update ready components
                if component_id in self.component_dependents:
                    for dependent_id in self.component_dependents[component_id]:
                        # Check if all dependencies of the dependent are completed
                        if dependent_id in self.component_dependencies:
                            dependencies = self.component_dependencies[dependent_id]
                            if all(dep_id in self.completed_components for dep_id in dependencies):
                                self.ready_components.add(dependent_id)
            except Exception as e:
                logger.error(f"Error executing component {component_id}: {e}")
                self.component_errors[component_id] = str(e)
                self.failed_components.add(component_id)
                
                # Log the execution
                self.execution.logs.append({
                    "component_id": component_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e)
                })
        
        # Set execution end time
        self.execution.end_time = datetime.datetime.now().isoformat()
        
        # Set execution status
        if self.failed_components:
            self.execution.status = "failed"
        else:
            self.execution.status = "completed"
        
        # Set execution results and errors
        self.execution.results = self.component_results
        self.execution.errors = self.component_errors
        
        return self.execution


class WorkflowExecutionManager:
    """Manager for workflow executions."""
    
    def __init__(self):
        self.executions = {}
    
    async def execute_workflow(self, workflow: Workflow, inputs: Dict[str, Any] = None, context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow with the given inputs and context."""
        executor = WorkflowExecutor(workflow)
        execution = await executor.execute(inputs, context)
        self.executions[execution.id] = execution
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID."""
        return self.executions.get(execution_id)
    
    def list_executions(self, workflow_id: Optional[str] = None) -> List[WorkflowExecution]:
        """List workflow executions, optionally filtered by workflow ID."""
        if workflow_id:
            return [execution for execution in self.executions.values() if execution.workflow_id == workflow_id]
        return list(self.executions.values())
