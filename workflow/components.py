"""
Component implementations for the workflow engine.
"""

import logging
import requests
from typing import Dict, List, Any, Optional, Callable
from .models import (
    Component, AgentComponent, PluginComponent, DataSourceComponent,
    InputComponent, OutputComponent, ComponentType
)

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Registry of available component types."""
    
    def __init__(self):
        self.components = {}
    
    def register(self, component_type: str, component_class):
        """Register a component type."""
        self.components[component_type] = component_class
    
    def get(self, component_type: str):
        """Get a component class by type."""
        return self.components.get(component_type)
    
    def list_components(self):
        """List all registered component types."""
        return list(self.components.keys())


# Global component registry
registry = ComponentRegistry()


class ComponentExecutor:
    """Base class for component executors."""
    
    def __init__(self, component: Component):
        self.component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the component with the given inputs and context."""
        raise NotImplementedError("Component executors must implement execute()")


class AgentExecutor(ComponentExecutor):
    """Executor for agent components."""
    
    def __init__(self, component: AgentComponent):
        super().__init__(component)
        self.agent_component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with the given inputs and context."""
        # Get the message from inputs
        message = inputs.get("message", "")
        history = inputs.get("history", [])
        
        # Get agent configuration
        agent_id = self.agent_component.agent_id
        api_url = self.agent_component.api_url
        api_key = self.agent_component.api_key
        model = self.agent_component.model
        
        # If agent_id is provided, use the agent service
        if agent_id:
            try:
                # Get the agent service URL from context
                agent_service_url = context.get("agent_service_url", "http://localhost:5000")
                
                # Call the agent service
                response = requests.post(
                    f"{agent_service_url}/api/chat",
                    json={
                        "message": message,
                        "history": history,
                        "agent_id": agent_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {
                        "message": response.json().get("message", ""),
                        "role": "assistant",
                        "agent_id": agent_id
                    }
                else:
                    logger.error(f"Error calling agent service: {response.text}")
                    return {
                        "error": f"Error calling agent service: {response.status_code}",
                        "details": response.text
                    }
            except Exception as e:
                logger.error(f"Error executing agent: {e}")
                return {"error": f"Error executing agent: {str(e)}"}
        
        # If no agent_id but API configuration is provided, call the API directly
        elif api_url and api_key and model:
            try:
                # Prepare messages for the API
                messages = []
                
                # Add system message if provided
                system_prompt = self.agent_component.system_prompt
                if system_prompt:
                    messages.append({
                        "role": "system",
                        "content": system_prompt
                    })
                
                # Add conversation history
                messages.extend(history)
                
                # Add the new message
                messages.append({
                    "role": "user",
                    "content": message
                })
                
                # Call the API
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                data = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        choice = response_data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            return {
                                "message": choice["message"]["content"],
                                "role": "assistant",
                                "usage": response_data.get("usage", {})
                            }
                
                logger.error(f"Error calling API: {response.text}")
                return {
                    "error": f"Error calling API: {response.status_code}",
                    "details": response.text
                }
            except Exception as e:
                logger.error(f"Error executing agent: {e}")
                return {"error": f"Error executing agent: {str(e)}"}
        
        # If no configuration is provided, return an error
        else:
            return {"error": "No agent configuration provided"}


class PluginExecutor(ComponentExecutor):
    """Executor for plugin components."""
    
    def __init__(self, component: PluginComponent):
        super().__init__(component)
        self.plugin_component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin with the given inputs and context."""
        # Get the plugin type
        plugin_type = self.plugin_component.plugin_type
        
        # Get the plugin executor from the registry
        plugin_executor = plugin_registry.get(plugin_type)
        if not plugin_executor:
            return {"error": f"Unknown plugin type: {plugin_type}"}
        
        # Execute the plugin
        try:
            return await plugin_executor(self.plugin_component, inputs, context)
        except Exception as e:
            logger.error(f"Error executing plugin: {e}")
            return {"error": f"Error executing plugin: {str(e)}"}


class DataSourceExecutor(ComponentExecutor):
    """Executor for data source components."""
    
    def __init__(self, component: DataSourceComponent):
        super().__init__(component)
        self.data_source_component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the data source with the given inputs and context."""
        # Get the data source type
        source_type = self.data_source_component.source_type
        
        # Get the data source executor from the registry
        source_executor = data_source_registry.get(source_type)
        if not source_executor:
            return {"error": f"Unknown data source type: {source_type}"}
        
        # Execute the data source
        try:
            return await source_executor(self.data_source_component, inputs, context)
        except Exception as e:
            logger.error(f"Error executing data source: {e}")
            return {"error": f"Error executing data source: {str(e)}"}


class InputExecutor(ComponentExecutor):
    """Executor for input components."""
    
    def __init__(self, component: InputComponent):
        super().__init__(component)
        self.input_component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the input component with the given inputs and context."""
        # Simply pass through the inputs
        return inputs


class OutputExecutor(ComponentExecutor):
    """Executor for output components."""
    
    def __init__(self, component: OutputComponent):
        super().__init__(component)
        self.output_component = component
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the output component with the given inputs and context."""
        # Simply pass through the inputs
        return inputs


# Register component executors
registry.register(ComponentType.AGENT, AgentExecutor)
registry.register(ComponentType.PLUGIN, PluginExecutor)
registry.register(ComponentType.DATA_SOURCE, DataSourceExecutor)
registry.register(ComponentType.INPUT, InputExecutor)
registry.register(ComponentType.OUTPUT, OutputExecutor)


# Plugin registry
plugin_registry = {}


def register_plugin(plugin_type: str, executor_func: Callable):
    """Register a plugin executor."""
    plugin_registry[plugin_type] = executor_func


# Data source registry
data_source_registry = {}


def register_data_source(source_type: str, executor_func: Callable):
    """Register a data source executor."""
    data_source_registry[source_type] = executor_func


# Register some basic plugins

async def web_search_plugin(component: PluginComponent, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Web search plugin."""
    query = inputs.get("query", "")
    if not query:
        return {"error": "No query provided"}
    
    try:
        # Simple mock implementation
        return {
            "results": [
                {"title": f"Result for {query} 1", "url": f"https://example.com/1", "snippet": f"This is a result for {query}"},
                {"title": f"Result for {query} 2", "url": f"https://example.com/2", "snippet": f"Another result for {query}"}
            ]
        }
    except Exception as e:
        return {"error": f"Error executing web search: {str(e)}"}

register_plugin("web_search", web_search_plugin)


async def document_data_source(component: DataSourceComponent, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Document data source."""
    query = inputs.get("query", "")
    if not query:
        return {"error": "No query provided"}
    
    try:
        # Simple mock implementation
        return {
            "documents": [
                {"title": f"Document 1", "content": f"This document contains information about {query}"},
                {"title": f"Document 2", "content": f"More information about {query} in this document"}
            ]
        }
    except Exception as e:
        return {"error": f"Error retrieving documents: {str(e)}"}

register_data_source("document", document_data_source)
