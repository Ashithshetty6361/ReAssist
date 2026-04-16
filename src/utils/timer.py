"""
Timer utility for measuring agent execution time
Provides context manager and decorator for timing operations
"""

import time
from functools import wraps
from utils.logger import get_logger


class Timer:
    """Context manager for timing code blocks"""
    
    def __init__(self, name="Operation"):
        """Initialize timer with operation name"""
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        """Start timer"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """End timer and calculate duration"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return False
    
    def get_duration(self):
        """Get duration in seconds"""
        return self.duration if self.duration else 0


def time_agent(agent_name):
    """
    Decorator for timing agent functions
    
    Args:
        agent_name: Name of the agent being timed
    
    Usage:
        @time_agent("SearchAgent")
        def search_papers(query):
            # agent code
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            logger.log_agent_start(agent_name)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_agent_end(agent_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_error(f"{agent_name} failed after {duration:.2f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator


class AgentTimer:
    """Simple timer for tracking agent execution"""
    
    def __init__(self):
        self.timings = {}
    
    def start(self, agent_name):
        """Start timing an agent"""
        self.timings[agent_name] = {"start": time.time()}
    
    def stop(self, agent_name):
        """Stop timing an agent and return duration"""
        if agent_name in self.timings:
            duration = time.time() - self.timings[agent_name]["start"]
            self.timings[agent_name]["duration"] = duration
            return duration
        return 0
    
    def get_duration(self, agent_name):
        """Get duration for specific agent"""
        return self.timings.get(agent_name, {}).get("duration", 0)
    
    def get_all_timings(self):
        """Get all agent timings"""
        return {name: data.get("duration", 0) for name, data in self.timings.items()}
    
    def get_total_time(self):
        """Get total execution time across all agents"""
        return sum(data.get("duration", 0) for data in self.timings.values())
