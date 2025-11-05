# Mock loguru module for compatibility
class Logger:
    def __init__(self):
        pass
    
    def debug(self, msg):
        print(f"[DEBUG] {msg}")
    
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def warning(self, msg):
        print(f"[WARNING] {msg}")
    
    def error(self, msg):
        print(f"[ERROR] {msg}")
    
    def success(self, msg):
        print(f"[SUCCESS] {msg}")

logger = Logger()

# Mock other common loguru functions
def add(sink, **kwargs):
    pass

def remove(handler_id):
    pass

def configure(**kwargs):
    pass