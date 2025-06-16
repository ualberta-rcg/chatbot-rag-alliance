from flask import current_app
from utils.handlers import SocketIOCallbackHandler

class HandlerManager:
    def __init__(self):
        self.handlers = {}
    
    def add_handler(self, sid):
        try:
            handler = SocketIOCallbackHandler(sid)
            self.handlers[sid] = handler
            return handler
        except Exception as e:
            current_app.logger.error(f"Error creating handler for sid {sid}: {str(e)}")
            raise
        
    def get_handler(self, sid):
        if sid not in self.handlers:
            return self.add_handler(sid)
        return self.handlers.get(sid)
        
    def remove_handler(self, sid):
        try:
            if sid in self.handlers:
                del self.handlers[sid]
        except Exception as e:
            current_app.logger.error(f"Error removing handler for sid {sid}: {str(e)}")
            
    def stop_handler(self, sid):
        try:
            if sid in self.handlers:
                self.handlers[sid].stop_streaming()
                self.remove_handler(sid)
        except Exception as e:
            current_app.logger.error(f"Error stopping handler for sid {sid}: {str(e)}")
