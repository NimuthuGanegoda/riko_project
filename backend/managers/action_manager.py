import os
import webbrowser
import subprocess
import datetime
import logging
import json
import re

logger = logging.getLogger(__name__)

class ActionManager:
    def __init__(self):
        self.available_actions = {
            "open_website": self.open_website,
            "get_time": self.get_time,
            "launch_app": self.launch_app
        }

    def get_system_prompt_addition(self):
        return """
        [System: You are now an active virtual assistant (like Cortana or Google Assistant).
        If the user asks you to open a website, check the time, or launch an app,
        you MUST include an action tag at the very end of your response.
        Format: [ACTION: {"action": "action_name", "param": "parameter"}]
        Available actions:
        - {"action": "open_website", "param": "url (e.g., youtube.com, github.com)"}
        - {"action": "get_time", "param": ""}
        - {"action": "launch_app", "param": "app name (e.g., notepad, calculator, calc)"}
        
        Example 1: 
        User: Open youtube
        Riko: Sure senpai, I'll open YouTube for you right now! [ACTION: {"action": "open_website", "param": "youtube.com"}]
        
        Example 2:
        User: What time is it?
        Riko: Let me check the clock for you. [ACTION: {"action": "get_time", "param": ""}]
        ]
        """

    def parse_and_execute(self, response_text):
        """
        Parses the response for an action tag and executes it.
        Returns the modified text (with tag removed) and any execution result.
        """
        match = re.search(r'\[ACTION:\s*({.*?})\s*\]', response_text)
        if match:
            action_json_str = match.group(1)
            try:
                action_data = json.loads(action_json_str)
                action_name = action_data.get("action")
                param = action_data.get("param")
                
                clean_text = response_text.replace(match.group(0), "").strip()
                
                if action_name in self.available_actions:
                    logger.info(f"Executing action: {action_name} with param: {param}")
                    if param:
                        result = self.available_actions[action_name](param)
                    else:
                        result = self.available_actions[action_name]()
                    
                    return clean_text, result
                else:
                    return clean_text, f"Unknown action: {action_name}"
            except Exception as e:
                logger.error(f"Failed to parse or execute action: {e}")
                return response_text, None
        return response_text, None

    def open_website(self, url):
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Successfully opened {url} in the browser."

    def get_time(self):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current system time is {now}."

    def launch_app(self, app_name):
        try:
            if os.name == 'nt': # Windows
                os.system(f'start {app_name}')
            elif os.uname().sysname == 'Darwin': # macOS
                subprocess.Popen(['open', '-a', app_name])
            else: # Linux
                subprocess.Popen([app_name])
            return f"Successfully launched {app_name}."
        except Exception as e:
            return f"Failed to launch {app_name}: {e}"
