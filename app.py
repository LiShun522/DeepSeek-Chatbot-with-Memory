import os
import logging
import time
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ShowLoadingAnimationRequest
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from modules.response_generator import ResponseGenerator
from modules.memory_manager import MemoryManager

# 載入環境變數
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# LINE API 配置
access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")

configuration = Configuration(access_token=access_token)
handler = WebhookHandler(secret)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

# 初始化 ChatOllama 模型
llm = ChatOllama(model="deepseek-r1:8b", temperature=0.7, num_predict=1000)

# 初始化回應生成器 & 記憶管理
response_generator = ResponseGenerator()
memory_manager = MemoryManager()

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    session_id = event.source.user_id  # 用戶 ID 作為 session_id

    # 判斷 chatId（根據聊天類型）
    if event.source.type == "user":
        chat_id = event.source.user_id  # 單人對話
    elif event.source.type == "group":
        chat_id = event.source.group_id  # 群組對話
    elif event.source.type == "room":
        chat_id = event.source.room_id  # 多人聊天室對話
    else:
        logger.error("無法識別的聊天來源")
        return

    try:
        # **(1) 發送「打字中」動畫**
        loading_request = ShowLoadingAnimationRequest(
            chat_id=chat_id  # 修正這裡，提供正確的 chatId
        )
        line_bot_api.show_loading_animation(loading_request)

        # **(2) 生成回應**
        start_time = time.time()
        bot_response = response_generator.generate_response(session_id, memory_manager, user_message)
        end_time = time.time()

        logger.info(f"回應生成時間: {end_time - start_time:.2f} 秒")

        # **(3) 發送最終回應**
        reply_request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=bot_response)]
        )
        line_bot_api.reply_message(reply_request)

    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {e}")
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="抱歉，發生錯誤，請稍後再試！")]
            )
        )


if __name__ == "__main__":
    app.run()
