"""
Plugin manager for the Sujin framework.
"""

from typing import Dict, List, Optional, Any, Type
import importlib
import logging
import pkgutil
import inspect

from .base import Plugin, PluginConfig
from ..core.models import AgentInput, AgentOutput


logger = logging.getLogger(__name__)


class PluginManager:
    """Manager for loading and running plugins."""
    
    def __init__(self):
        """Initialize a new PluginManager."""
        self.plugins: Dict[str, Plugin] = {}
        
    def register_plugin(self, plugin: Plugin) -> None:
        """
        Register a plugin with the manager.
        
        Args:
            plugin: The plugin to register
        """
        if plugin.name in self.plugins:
            logger.warning(f"Plugin {plugin.name} is already registered. Overwriting.")
        
        self.plugins[plugin.name] = plugin
        plugin.on_load()
        logger.info(f"Registered plugin: {plugin.name}")
        
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin from the manager.
        
        Args:
            plugin_name: The name of the plugin to unregister
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} is not registered.")
            return
            
        plugin = self.plugins[plugin_name]
        plugin.on_unload()
        del self.plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: The name of the plugin to get
            
        Returns:
            The plugin, or None if it's not registered
        """
        return self.plugins.get(plugin_name)
        
    def discover_plugins(self, package_name: str = "sujin.plugins") -> None:
        """
        Discover and register plugins from a package.
        
        Args:
            package_name: The name of the package to search for plugins
        """
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.error(f"Could not import package {package_name}")
            return
            
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            if is_pkg:
                self.discover_plugins(name)
                continue
                
            try:
                module = importlib.import_module(name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, Plugin) 
                        and obj is not Plugin 
                        and not inspect.isabstract(obj)
                    ):
                        self.register_plugin(obj())
            except (ImportError, AttributeError) as e:
                logger.error(f"Error loading plugin from {name}: {e}")
                
    def run_pre_process(self, input_data: AgentInput) -> AgentInput:
        """
        Run pre-processing on input data using all registered plugins.
        
        Args:
            input_data: The input data to pre-process
            
        Returns:
            The pre-processed input data
        """
        # Sort plugins by priority (highest first)
        sorted_plugins = sorted(
            [p for p in self.plugins.values() if p.enabled],
            key=lambda p: p.priority,
            reverse=True
        )
        
        result = input_data
        for plugin in sorted_plugins:
            try:
                result = plugin.pre_process(result)
            except Exception as e:
                logger.error(f"Error in plugin {plugin.name} pre_process: {e}")
                
        return result
        
    def run_post_process(self, output_data: AgentOutput) -> AgentOutput:
        """
        Run post-processing on output data using all registered plugins.
        
        Args:
            output_data: The output data to post-process
            
        Returns:
            The post-processed output data
        """
        # Sort plugins by priority (highest first)
        sorted_plugins = sorted(
            [p for p in self.plugins.values() if p.enabled],
            key=lambda p: p.priority,
            reverse=True
        )
        
        result = output_data
        for plugin in sorted_plugins:
            try:
                result = plugin.post_process(result)
            except Exception as e:
                logger.error(f"Error in plugin {plugin.name} post_process: {e}")
                
        return result
        
    def handle_error(self, error: Exception, input_data: AgentInput) -> Optional[AgentOutput]:
        """
        Handle an error using registered plugins.
        
        Args:
            error: The error that occurred
            input_data: The input data that caused the error
            
        Returns:
            An optional output to return instead of raising the error
        """
        # Sort plugins by priority (highest first)
        sorted_plugins = sorted(
            [p for p in self.plugins.values() if p.enabled],
            key=lambda p: p.priority,
            reverse=True
        )
        
        for plugin in sorted_plugins:
            try:
                result = plugin.on_error(error, input_data)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"Error in plugin {plugin.name} on_error: {e}")
                
        return None
