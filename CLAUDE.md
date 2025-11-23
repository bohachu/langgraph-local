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
   - 模型: gemma-3n-e4b-it-mlx

### 啟動方式
```bash
./start.sh
# 或
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

## 未來擴充方向
1. 加入更多 MCP servers (bash, ripgrep)
2. 實作對話持久化 (LangGraph checkpoint)
3. 建立 Web UI (Streamlit/Gradio)
4. 優化 state_modifier prompt
