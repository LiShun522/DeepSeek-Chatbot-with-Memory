import logging
from langchain.memory import ConversationBufferWindowMemory
from pprint import pformat

class MemoryManager:
    def __init__(self):
        self.user_memory = {}

    def get_or_create_memory(self, session_id):
        # 如果記憶不存在，則創建新的記憶
        if session_id not in self.user_memory:
            self.user_memory[session_id] = ConversationBufferWindowMemory(k=10, return_messages=True)
            logging.info(f"創建新的記憶體 session_id: {session_id}")
        return self.user_memory[session_id]

    def log_conversation_memory(self, session_id):
        """日誌記錄記憶中的對話記錄"""
        memory = self.get_or_create_memory(session_id)
        history = memory.load_memory_variables({}).get('history', [])
        logging.info(f"當前對話歷史 session_id: {session_id}: {pformat(history)}")

    def save_to_memory(self, session_id, input_text, output_text):
        memory = self.get_or_create_memory(session_id)
        memory.save_context({"input": input_text}, {"output": output_text})
        logging.info(f"AI 回應加入記憶: {output_text}")

    def get_session_memory(self, session_id):
        """取得 session_id 對應的歷史對話記錄"""
        memory = self.get_or_create_memory(session_id)
        history = memory.load_memory_variables({}).get('history', [])
        # 返回對話歷史，如果沒有歷史則返回一個空訊息
        if history:
            return history
        else:
            return "無先前的對話記錄"
