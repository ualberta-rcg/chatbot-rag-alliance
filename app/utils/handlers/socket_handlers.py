# utils/handlers/socket_handlers.py

#from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from flask_socketio import emit

class SocketIOCallbackHandler(StreamingStdOutCallbackHandler):
    def __init__(self, socketio, conversation_id=None):
        self.socketio = socketio
        self.should_stop = False
        self.has_stopped = False
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs):
        if self.should_stop:
            if not self.has_stopped:
                self.has_stopped = True
                emit('chat_response_stopped', {
                    'stopped': True,
                })
            return  

        response_chunk = {
            'response_chunk': token,
        }
        emit('chat_response', response_chunk)
    
    def on_llm_end(self, *args, **kwargs):
        if not self.should_stop:
            emit('chat_response_end', {
                'end': True,
            })

    def stop_streaming(self):
        self.should_stop = True
        self.has_stopped = False  # Reset flag on stop for future use
