import json
from netmiko import ConnectHandler
import requests
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CiscoStateAnalyzer:
    def __init__(self, host: str, username: str, password: str, 
                 ollama_host: str = "http://localhost:11434"):
        """Initialize the analyzer with device and Ollama connection details."""
        self.device_config = {
            'device_type': 'cisco_ios',
            'host': host,
            'username': username,
            'password': password,
        }
        self.ollama_host = ollama_host

    def connect_to_device(self):
        """Establish connection to the Cisco device."""
        try:
            logger.info(f"Connecting to device {self.device_config['host']}")
            self.connection = ConnectHandler(**self.device_config)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {str(e)}")
            return False

    def get_multicast_state(self) -> Dict[str, List[str]]:
        """Gather multicast-related information from the device."""
        commands = [
            'show ip mroute',
            'show ip pim neighbor',
            'show ip igmp groups',
            'show ip mroute count'
        ]
        
        output = {}
        for command in commands:
            try:
                logger.info(f"Executing command: {command}")
                result = self.connection.send_command(command)
                output[command] = result.split('\n')
            except Exception as e:
                logger.error(f"Error executing {command}: {str(e)}")
                output[command] = [f"Error: {str(e)}"]
        
        return output

    def analyze_with_ollama(self, data: Dict[str, List[str]]) -> str:
        """Send data to Ollama for analysis and natural language summary."""
        prompt = """
        Analyze the following Cisco multicast state information and provide a clear, 
        concise summary that would help a network operator understand:
        1. The current multicast state
        2. Any potential issues or anomalies
        3. Key statistics and active groups

        Data:
        """
        
        # Format the data for the prompt
        formatted_data = "\n\n".join([f"{cmd}:\n" + "\n".join(output) 
                                    for cmd, output in data.items()])
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt + formatted_data,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error getting analysis: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {str(e)}")
            return f"Error analyzing data: {str(e)}"

    def close_connection(self):
        """Close the connection to the Cisco device."""
        if hasattr(self, 'connection'):
            self.connection.disconnect()

def main():
    # Device connection details
    device = {
        'host': 'your_device_ip',
        'username': 'your_username',
        'password': 'your_password'
    }
    
    analyzer = CiscoStateAnalyzer(**device)
    
    if analyzer.connect_to_device():
        try:
            # Gather multicast state
            multicast_state = analyzer.get_multicast_state()
            
            # Get analysis from Ollama
            analysis = analyzer.analyze_with_ollama(multicast_state)
            
            # Print the natural language summary
            print("\nMulticast State Analysis:")
            print("-" * 50)
            print(analysis)
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
        finally:
            analyzer.close_connection()

if __name__ == "__main__":
    main() 