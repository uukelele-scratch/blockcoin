import json

class Theme:
    def __init__(self, data):
        self.data = json.loads(data)
    
    def __str__(self):
        return f"{self.data['meta']['name']} by {self.data['meta']['author']}"
    
    def __repr__(self):
        return self.data["meta"]["key"]