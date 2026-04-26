import os
import json
import logging

logger = logging.getLogger(__name__)

class FactManager:
    def __init__(self, storage_path="configs/user_facts.json"):
        self.storage_path = storage_path
        self.facts = self._load_facts()

    def _load_facts(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {"name": "Senpai", "interests": [], "important_dates": {}, "notes": {}}

    def _save_facts(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.facts, f, indent=4)

    def extract_and_update(self, text, response, llm):
        """
        Asks the LLM to identify any NEW facts about the user from the exchange.
        This is the 'Mem0' style autonomous learning.
        """
        prompt = f"""
        Extract any new personal facts, preferences, or details about the user from this exchange.
        Current facts: {json.dumps(self.facts)}
        
        User: {text}
        Assistant: {response}
        
        Return ONLY a JSON object with any UPDATED or NEW fields for the user profile. 
        If nothing new, return an empty object {{}}.
        """
        try:
            # We use a simplified internal call to get the JSON
            # In a real scenario, we might use a smaller model to save costs
            update_json_str = llm.generate([{"role": "system", "content": "You are a data extractor. Return JSON ONLY."}, {"role": "user", "content": prompt}])
            
            # Clean JSON string (handle potential markdown)
            clean_json = update_json_str.strip().replace("```json", "").replace("```", "")
            updates = json.loads(clean_json)
            
            if updates:
                logger.info(f"Updated user facts: {updates}")
                self._update_nested_dict(self.facts, updates)
                self._save_facts()
        except Exception as e:
            logger.error(f"Failed to update facts: {e}")

    def _update_nested_dict(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            elif isinstance(v, list):
                d[k] = list(set(d.get(k, []) + v)) # Merge lists without duplicates
            else:
                d[k] = v
        return d

    def get_fact_prompt(self):
        return f"[System Memory: Key facts about Senpai: {json.dumps(self.facts)}]"
