import logging
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ResponseGenerator:
    def __init__(self):
        self.llm = ChatOllama(model="deepseek-r1:8b", temperature=0.7, num_predict=1000)

    def construct_prompt(self, conversation, user_question):
        """
        優化提示詞，確保 AI 回應更精準且有條理
        """
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="""
                    你是一位專業且可靠的助理，負責提供準確且簡潔的回答，請遵循以下規則：
                    1. **請使用繁體中文回覆**。
                    2. **回答應該清晰、具結構化（條列式）、避免冗長**。
                    3. **如果問題超出你的知識範圍，請誠實回答「不知道」，而不是胡亂編造**。
                    4. **避免重複使用稱呼詞**，直接進入回答。
                    5. **當問題過於模糊時，請詢問使用者是否需要更明確的解釋**。
                    6. **提供解釋時，確保資訊正確，並避免多餘的修飾或過度解釋**。
                    7. **請確保回答符合上下文，不要無視對話歷史**。
                """),
                MessagesPlaceholder(variable_name="conversation"),
                HumanMessage(content=f"使用者的最新問題：{user_question}")
            ]
        )
        prompt_value = prompt_template.format_prompt(conversation=conversation)
        logging.info(f"構建的提示語: {prompt_value.to_string()}")
        return prompt_value.to_messages()

    def convert_to_message_objects(self, conversation):
        """將對話記憶轉換為訊息物件"""
        converted_conversation = []
        for msg in conversation:
            role = msg.get('role')
            content = msg.get('content')
            if role == 'system':
                converted_conversation.append(SystemMessage(content=content))
            elif role == 'user':
                converted_conversation.append(HumanMessage(content=content))
            elif role == 'assistant':
                converted_conversation.append(AIMessage(content=content))
        return converted_conversation

    def generate_response(self, session_id, memory_manager, user_question):
        try:
            # 獲取對話記憶
            memory = memory_manager.get_or_create_memory(session_id)
            conversation = memory.load_memory_variables({}).get('history', [])

            # 確保對話記憶是訊息物件列表
            if not all(isinstance(msg, (SystemMessage, HumanMessage, AIMessage)) for msg in conversation):
                conversation = self.convert_to_message_objects(conversation)

            # 構建提示語，取得訊息列表
            messages = self.construct_prompt(conversation, user_question)

            logging.info(f"傳遞給 LLM 的訊息列表：{messages}")

            # 使用 Ollama 模型生成回應
            response = self.llm.invoke(messages)

            # 檢查是否生成了空回應
            if not response.content.strip():
                logging.error("收到空回應，回應不保存到記憶中")
                return "抱歉，AI 無法生成有效回應，請再試一次。"

            # # 移除 <think> ... </think> 內容（確保回應純淨）
            clean_response = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()

            # 確保回應不為空
            if not clean_response:
                logging.error("清理後的回應為空，回應不保存到記憶中")
                return "抱歉，AI 無法生成有效回應，請再試一次。"

            # 將使用者的提問和 AI 的回應保存到記憶中
            memory_manager.save_to_memory(session_id, user_question, clean_response)

            return clean_response
        
        except ValueError as ve:
            logging.error(f"值錯誤發生: {str(ve)}")
            return "發生值錯誤，請稍後再試。"
        except TypeError as te:
            logging.error(f"類型錯誤發生: {str(te)}")
            return "發生類型錯誤，請稍後再試。"
        except Exception as e:
            logging.error(f"回應生成過程中發生不明錯誤: {str(e)}")
            return "系統發生錯誤，請稍後再試。"
