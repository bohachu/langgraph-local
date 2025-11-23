# Claude Code 專案記憶

## 專案資訊
- **專案名稱**: langgraph-local
- **目的**: 建立類似 Claude Code 的 Agentic AI，使用 LangGraph + MCP + 本地 LM Studio
- **建立日期**: 2025-11-23

## 地雷經驗記憶

### Agentic AI 實作地雷
- **參考時機**: 當需要實作自主執行的 AI Agent、整合 LangGraph + MCP、或建立類似 Claude Code 的工具時
- **文件位置**: `/Users/40gpu/coding_projects/langgraph-local/docs/地雷-LangGraph-MCP-整合.txt`
- **核心要點**:
  - 使用 `create_react_agent` 建立 ReAct 循環（推理→行動→觀察）
  - 設定 `state_modifier` 明確指示 Agent 要自主執行
  - MCP filesystem server 需要明確指定工作目錄路徑
  - 模型至少需要 4B 參數才有足夠推理能力

### LM Studio Function Calling 模型選擇地雷 ⚠️ 重要！
- **參考時機**: 選擇 LM Studio 模型時、工具調用無法正常工作時、看到 `StructuredTool does not support sync invocation` 錯誤時
- **文件位置**: `/Users/40gpu/coding_projects/langgraph-local/docs/地雷-LM-Studio-Function-Calling-模型選擇.txt`
- **核心要點**:
  - ✅ **使用 gpt-oss-20b**（原生支援 function calling）
  - ⚠️ **不要使用 gemma-3n**（不支援原生 function calling，只會輸出 JSON 文字）
  - 其他支援的模型：qwen2.5, mistral, llama-3.1/3.2
  - MCP 工具 schema 必須包含 `type`, `properties`, `required` 欄位
  - 在 async 環境中必須使用 `await agent.ainvoke()`，不能用同步的 `invoke()`

## 技術架構

### 核心元件
1. **LangGraph ReAct Agent** (`agent.py`)
   - 使用 `create_react_agent` 建立自主執行循環
   - 整合 MCP tools 作為 Agent 的工具

2. **MCP Integration**
   - 使用 `langchain-mcp-adapters` 的 `MultiServerMCPClient`
   - 目前支援: filesystem operations
   - 可擴充: bash, ripgrep 等

3. **Terminal Client** (`chat_client.py`)
   - 互動式對話介面
   - 支援多輪對話記憶
   - 指令系統: /help, /info, /clear, /exit

4. **LM Studio Integration**
   - 使用 OpenAI compatible API (localhost:1234)
   - 模型: **gpt-oss-20b-mlx** (✅ 原生支援 function calling)
   - 舊模型: ~~gemma-3n-e4b-it-mlx~~ (⚠️ 不支援 function calling)

### 啟動方式

**Server + Client 模式（推薦）**:
```bash
# 啟動 Server（背景執行）
./sh/server.sh

# 啟動 Client（另一個終端機）
./sh/client.sh
```

**獨立 CLI 模式**:
```bash
python3 chat_client.py
```

## Agentic 行為特徵

### ✅ 正確的 Agentic 行為
- 給意圖就自動規劃多步驟
- 自主決定呼叫哪些工具
- 不反問使用者細節
- 循環執行直到完成任務

### ❌ 要避免的傳統 Chatbot 行為
- 需要逐步指導
- 反問「請問您要...？」
- 單次請求-回應
- 不主動使用工具

## 測試驗證

### ✅ 成功案例（gpt-oss-20b）
```bash
curl -X POST http://localhost:8011/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "請列出當前目錄有哪些 Python 檔案？"}'
```

**成功指標**：
- ✅ 執行軌跡顯示 `🔧 Agent 呼叫工具: ['list_directory']`
- ✅ 顯示 `📊 工具結果`
- ✅ 最終回應包含實際的檔案列表（agent.py, server.py 等）

### ❌ 失敗案例（gemma-3n）
- 只輸出 `tool_request` 的 JSON 文字
- 沒有實際的工具調用軌跡
- 無法完成 ReAct 循環

## 未來擴充方向
1. 加入更多 MCP servers (bash, ripgrep)
2. 實作對話持久化 (LangGraph checkpoint)
3. 建立 Web UI (Streamlit/Gradio)
4. 優化 state_modifier prompt
5. 支援更多 function calling 模型
