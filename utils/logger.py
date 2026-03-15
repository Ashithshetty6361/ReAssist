"""
Logger utility for Research Intelligence Engine
Provides structured logging for all agent activities
"""

import logging
import os
from datetime import datetime
import json


class ResearchLogger:
    """Custom logger for tracking research pipeline execution"""
    
    def __init__(self, log_dir="logs"):
        """Initialize logger with timestamped log file"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"research_log_{timestamp}.log")
        self.json_file = os.path.join(log_dir, f"research_log_{timestamp}.json")
        
        # Set up file logger
        self.logger = logging.getLogger("ResearchEngine")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Initialize structured log data
        self.log_data = {
            "timestamp": timestamp,
            "user_query": None,
            "papers_found": 0,
            "agent_timings": {},
            "errors": [],
            "results": {}
        }
    
    def log_query(self, query):
        """Log user query"""
        self.log_data["user_query"] = query
        self.logger.info(f"User Query: {query}")
    
    def log_papers_found(self, count):
        """Log number of papers found"""
        self.log_data["papers_found"] = count
        self.logger.info(f"Papers Found: {count}")
    
    def log_agent_start(self, agent_name):
        """Log agent execution start"""
        self.logger.info(f"Agent Started: {agent_name}")
    
    def log_agent_end(self, agent_name, duration):
        """Log agent execution end with timing"""
        self.log_data["agent_timings"][agent_name] = duration
        self.logger.info(f"Agent Completed: {agent_name} (Duration: {duration:.2f}s)")
    
    def log_error(self, error_message):
        """Log error"""
        self.log_data["errors"].append(error_message)
        self.logger.error(error_message)
    
    def log_result(self, key, value):
        """Log result data"""
        self.log_data["results"][key] = value
        self.logger.info(f"Result: {key}")
    
    def save_json_log(self):
        """Save structured log data to JSON file"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Structured log saved to: {self.json_file}")
    
    def get_log_summary(self):
        """Return summary of execution"""
        total_time = sum(self.log_data["agent_timings"].values())
        return {
            "query": self.log_data["user_query"],
            "papers_found": self.log_data["papers_found"],
            "total_time": total_time,
            "agent_count": len(self.log_data["agent_timings"]),
            "errors": len(self.log_data["errors"])
        }


# Global logger instance
_logger_instance = None


def get_logger():
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ResearchLogger()
    return _logger_instance


def reset_logger():
    """Reset logger for new session"""
    global _logger_instance
    _logger_instance = ResearchLogger()
    return _logger_instance
