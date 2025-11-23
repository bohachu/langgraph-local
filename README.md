# 🤖 Agentic AI Chat - LangGraph + MCP + LM Studio

類似 Claude Code 的自主執行 AI Agent，支援本地 LLM (LM Studio)

## ✨ 特色

- **🎯 自主多步驟執行** - 給意圖就自動完成，不需追問細節
- **🔧 工具使用能力** - 可讀寫檔案、執行 bash、搜尋程式碼
- **💬 多輪對話記憶** - 支援上下文理解
- **🏠 完全本地運行** - 使用 LM Studio，資料不外傳
- **⚡ ReAct Pattern** - 推理 → 行動 → 觀察的自主循環

## 🏗️ 架構

```
Terminal Client (chat_client.py)
    ↓
LangGraph ReAct Agent (agent.py)
    ↓
MCP Client (langchain-mcp-adapters)
    ↓ stdio
MCP Servers (filesystem, bash, ripgrep...)
    ↓ HTTP
LM Studio (localhost:1234)
    ↓
本地模型 (gemma-3n-e4b-it-mlx)
```

## 📋 前置需求

### 1. Python 3.10+
```bash
python3 --version
```

### 2. LM Studio
- 下載並安裝：https://lmstudio.ai
- 載入模型（建議：gemma-3n-e4b-it-mlx 或其他小型模型）
- 啟動 API Server（預設 port 1234）

### 3. Node.js (for MCP servers)
```bash
node --version  # v16+
```

## 🚀 快速開始

### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 2. 確認 LM Studio 正在運行
```bash
# 測試連線
curl http://localhost:1234/v1/models
```

### 3. 啟動 Chat Client
```bash
# 方式 1: 使用啟動腳本（推薦）
./start.sh

# 方式 2: 直接執行
python3 chat_client.py
```

## 💡 使用範例

### 基本使用
```
💬 你: 列出當前目錄的所有檔案

🤖 Agent 自動執行:
  1. 呼叫 list_directory 工具
  2. 分析結果
  3. 給出完整列表
```

### Agentic 行為範例
```
💬 你: 分析這個專案的 Python 檔案並統計總行數

🤖 Agent 自動執行:
  1. 列出目錄
  2. 過濾出 .py 檔案
  3. 逐一讀取每個檔案
  4. 統計行數
  5. 彙總報告

最終回答: "專案共有 5 個 Python 檔案，總計 1234 行程式碼..."
```

### 多輪對話
```
💬 你: 分析 agent.py

🤖 Agent: "agent.py 是一個 ReAct Agent 實作，共 150 行..."

💬 你: 它用了哪些主要的類別？

🤖 Agent: "主要類別是 AgenticChatBot，使用了..."
         (Agent 記得前面的檔案內容，不用重新讀取)
```

## 🎮 可用指令

在 Chat Client 中：

- `/help` - 顯示幫助訊息
- `/info` - 顯示當前狀態（對話 ID、工具數等）
- `/clear` - 清除對話記憶，開始新對話
- `/exit` 或 `/quit` - 離開程式

## 🔧 可用工具 (MCP)

目前支援的 MCP 工具：

- **filesystem** (已整合)
  - `read_file` - 讀取檔案
  - `write_file` - 寫入檔案
  - `list_directory` - 列出目錄
  - `create_directory` - 建立目錄
  - 等...

### 未來可擴充
在 `agent.py` 的 `mcp_client` 設定中加入：

```python
self.mcp_client = MultiServerMCPClient({
    "filesystem": {...},
    "bash": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-bash"]
    },
    "ripgrep": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-ripgrep"]
    }
})
```

## ⚙️ 設定

### 修改 LM Studio 端點
編輯 `agent.py`:
```python
agent = AgenticChatBot(
    base_url="http://localhost:1234/v1",  # 修改這裡
    model="your-model-name"                # 修改模型名稱
)
```

### 修改工作目錄
編輯 `agent.py`:
```python
"filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/path"]
}
```

## 🆚 與傳統 Chatbot 的差異

| 項目 | 傳統 Chatbot | Agentic AI (本專案) |
|------|-------------|-------------------|
| **行為** | 被動回答問題 | 主動執行任務 |
| **工具使用** | 需要明確指令 | 自主判斷使用時機 |
| **多步驟** | 需要逐步引導 | 自動規劃並執行 |
| **範例** | "請問要分析哪個檔案？" | 自動找檔案、分析、給報告 |

## 🐛 故障排除

### 問題：無法連接 LM Studio
```bash
# 檢查 LM Studio API Server 狀態
curl http://localhost:1234/v1/models

# 確認 LM Studio:
# 1. 已啟動
# 2. 模型已載入
# 3. API Server 已開啟（綠色按鈕）
```

### 問題：MCP 工具無法使用
```bash
# 確認 Node.js 已安裝
node --version

# 測試 MCP server
npx -y @modelcontextprotocol/server-filesystem .
```

### 問題：Agent 不夠 "agentic"
- 確認模型夠強（建議至少 4B 參數）
- 檢查 `agent.py` 中的 `state_modifier` prompt
- 降低 `temperature` 可能讓推理更穩定

## 📚 技術細節

### ReAct Pattern
```
使用者意圖
  ↓
Agent 推理 (Reasoning)
  ↓
執行工具 (Action)
  ↓
觀察結果 (Observation)
  ↓
再次推理...
  ↓
(循環直到完成)
  ↓
最終回答
```

### 核心元件
- **LangGraph**: 狀態圖框架，管理 Agent 流程
- **ReAct Agent**: `create_react_agent` 實作推理-行動循環
- **MCP**: Model Context Protocol，標準化工具介面
- **LM Studio**: 本地 LLM 伺服器

## 🔗 參考資源

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain MCP Adapters](https://docs.langchain.com/oss/python/langchain/mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [LM Studio](https://lmstudio.ai)
- [Building Agentic Flows with LangGraph and MCP](https://www.qodo.ai/blog/building-agentic-flows-with-langgraph-model-context-protocol/)

## 📝 授權

MIT License

---

**享受你的 Agentic AI 吧！ 🎉**

有問題或建議？歡迎開 Issue！
