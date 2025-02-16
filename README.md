# DeepSeek-Chatbot-with-Memory
🚀 一個基於 DeepSeek LLM 的 AI 回應生成系統，支援多輪對話記憶、等待動畫與智慧回應。

## 🔥 功能特色
- **DeepSeek AI 模型**：使用 `deepseek-r1:8b` 進行對話回應
- **LangChain 整合**：管理對話記憶，提高回應品質
- **LINE Bot 互動**：整合 LINE API，可部署為聊天機器人
- **等待動畫**：在 LLM 回應前，顯示「打字中」動畫，提高使用者體驗
- **錯誤處理機制**：應對 API 失敗、空回應等異常狀況

## 🚀 快速開始
請在資料夾內設立.env檔案
內容包含
# deepseek-r1:8b LINEBOT測試機器人 CHANNEL_ACCESS_TOKEN 與 CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN= <your LINE_CHANNEL_ACCESS_TOKEN>
LINE_CHANNEL_SECRET= <your LINE_CHANNEL_SECRET>
