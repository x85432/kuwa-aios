from typing import List, Optional

class BaseChunk:
    def __init__(self, cost:int|None=None):
        self.cost = cost

    def __jsonencode__(self):
        raise NotImplementedError()

    def calculate_cost(self):
        raise NotImplementedError()

    def __len__(self):
        return self.cost if self.cost is not None else self.calculate_cost()

class TextChunk(BaseChunk):
    def __init__(self, value: str, annotations: Optional[List] = None, cost:int|None=None):
        super().__init__(cost)
        self.value = value
        self.annotations = annotations if annotations is not None else []
        self.cost = cost

    def __jsonencode__(self):
        return {"type": "text", "text": {"value": self.value, "annotations": self.annotations}}

    def calculate_cost(self):
        return len(self.value)

class ImageURLChunk(BaseChunk):
    def __init__(self, image_url: str, cost:int|None=None):
        super().__init__(cost)
        self.image_url = image_url
        self.cost = cost

    def __jsonencode__(self):
        return {"type": "image_url", "image_url": self.image_url}
    
    def calculate_cost(self):
        return 0

class AudioURLChunk(BaseChunk):
    def __init__(self, audio_url: str, cost:int|None=None):
        super().__init__(cost)
        self.audio_url = audio_url
        self.cost = cost

    def __jsonencode__(self):
        return {"type": "audio_url", "audio_url": self.audio_url}
    
    def calculate_cost(self):
        return 0
    
class LogChunk(BaseChunk):
    def __init__(self, log: str, cost:int|None=None):
        super().__init__(cost)
        self.log = log

    def __jsonencode__(self):
        return {"type": "log", "log": self.log}
    
    def calculate_cost(self):
        return 0

class ProgressChunk(BaseChunk):
    def __init__(self, position: int, total: int, desc: Optional[str] = None, postfix: Optional[str] = None, cost:int|None=None):
        super().__init__(cost)
        self.position = position
        self.total = total
        self.desc = desc
        self.postfix = postfix

    def __jsonencode__(self):
        return {"type": "progress", "progress": {"position": self.position, "total": self.total, "desc": self.desc, "postfix": self.postfix}}

    def calculate_cost(self):
        return 0