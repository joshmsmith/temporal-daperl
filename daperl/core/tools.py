"""Base tool infrastructure for DAPERL framework."""

import logging
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


class ToolInfo:
    """Information about a tool."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: list[str],
        domain: str,
        tool_class: type
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.domain = domain
        self.tool_class = tool_class


class BaseTool(ABC):
    """Base class for all tools in the DAPERL framework."""
    
    def __init__(self, domain: str = "default"):
        """Initialize the tool.
        
        Args:
            domain: The domain this tool operates in
        """
        self.domain = domain
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given arguments.
        
        Args:
            arguments: Dictionary of arguments for the tool
            
        Returns:
            Dictionary containing the execution result
        """
        pass
    
    @abstractmethod
    def get_info(self) -> ToolInfo:
        """Get information about this tool.
        
        Returns:
            ToolInfo object describing the tool
        """
        pass
    
    def create_response(
        self,
        success: bool,
        data: Dict[str, Any],
        additional_notes: str = ""
    ) -> Dict[str, Any]:
        """Create a standardized response format.
        
        Args:
            success: Whether the operation was successful
            data: The result data
            additional_notes: Optional notes about the execution
            
        Returns:
            Standardized response dictionary
        """
        return {
            "success": success,
            "data": data,
            "message": additional_notes
        }


class ToolRegistry:
    """Registry for managing tools across different domains."""
    
    _tools: Dict[str, Dict[str, type]] = {}  # domain -> tool_name -> tool_class
    
    @classmethod
    def register_tool(cls, tool_class: type, domain: str = "default"):
        """Register a tool class for a domain.
        
        Args:
            tool_class: The tool class to register
            domain: The domain to register it under
        """
        if domain not in cls._tools:
            cls._tools[domain] = {}
        
        # Create a temporary instance to get the tool info
        temp_instance = tool_class(domain=domain)
        tool_info = temp_instance.get_info()
        
        cls._tools[domain][tool_info.name] = tool_class
    
    @classmethod
    def get_tool(cls, tool_name: str, domain: str = "default") -> Optional[type]:
        """Get a tool class by name and domain.
        
        Args:
            tool_name: Name of the tool
            domain: Domain to look in
            
        Returns:
            The tool class if found, None otherwise
        """
        return cls._tools.get(domain, {}).get(tool_name)
    
    @classmethod
    def get_tools_for_domain(cls, domain: str) -> list[Dict[str, Any]]:
        """Get all tools registered for a domain.
        
        Args:
            domain: The domain to get tools for
            
        Returns:
            List of tool information dictionaries
        """
        tools = []
        for tool_name, tool_class in cls._tools.get(domain, {}).items():
            temp_instance = tool_class(domain=domain)
            tool_info = temp_instance.get_info()
            tools.append({
                "name": tool_info.name,
                "description": tool_info.description,
                "parameters": tool_info.parameters
            })
        return tools
    
    @classmethod
    def create_action_registry(
        cls,
        available_actions: list[str],
        domain: str = "default"
    ) -> Dict[str, Callable]:
        """Create an action registry from available action names.
        
        Args:
            available_actions: List of action names to include
            domain: Domain to get tools from
            
        Returns:
            Dictionary mapping action names to async handler functions
        """
        action_registry = {}
        
        for action_name in available_actions:
            tool_class = cls.get_tool(action_name, domain)
            if tool_class:
                # Create a closure to capture the tool_class properly
                def make_handler(tool_cls, dom):
                    async def handler(action, context):
                        """Handler function for executing a tool."""
                        tool_instance = tool_cls(domain=dom)
                        # Action model has 'parameters' field, not 'arguments'
                        result = await tool_instance.execute(action.parameters)
                        return result
                    return handler
                
                # Create the handler and add to registry
                action_registry[action_name] = make_handler(tool_class, domain)
        
        return action_registry
