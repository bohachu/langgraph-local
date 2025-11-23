# 📘 使用總結 - Server/Client 架構

## 🎯 快速啟動指令

### 方式一：單機模式
```bash
./start.sh
```
適合：快速測試、個人使用

### 方式二：Server/Client 模式

**啟動 Server（終端機 1）:**
```bash
./sh/server.sh
```

**啟動 Client（終端機 2）:**
```bash
./sh/client.sh
```

**測試 Server:**
```bash
./sh/test.sh
```

## 📁 檔案架構總覽

```
langgraph-local/
├── 核心程式
│   ├── agent.py              # ReAct Agent 核心（共用）
│   ├── server.py             # FastAPI Server（新增）
│   ├── client_remote.py      # 遠端 Client（新增）
│   └── chat_client.py        # 本地 Client（原有）
│
├── 啟動腳本
│   ├── start.sh              # 單機模式啟動
│   └── sh/
│       ├── server.sh         # Server 啟動（新增）
│       ├── client.sh         # Client 啟動（新增）
│       └── test.sh           # 測試腳本（新增）
│
└── 文檔
    ├── README.md             # 主要文檔（已更新）
    ├── SERVER_CLIENT_GUIDE.md    # Server/Client 詳細指南（新增）
    ├── QUICKSTART.md         # 快速開始
    └── 專案總結.md           # 專案總結
```

## 🔄 兩種模式比較

| 項目 | 單機模式 | Server/Client 模式 |
|------|---------|-------------------|
| **啟動指令** | `./start.sh` | `./sh/server.sh` + `./sh/client.sh` |
| **適合場景** | 快速測試、個人使用 | 團隊協作、遠端存取 |
| **多客戶端** | ❌ | ✅ |
| **API 介面** | ❌ | ✅ (FastAPI) |
| **複雜度** | 低 | 中 |
| **遠端連接** | ❌ | ✅ |

## 🌐 Server API 端點

當 Server 運行時，可用以下 API：

### 基本資訊
- `GET /` - 服務資訊
- `GET /health` - 健康檢查
- `GET /status` - 伺服器狀態

### 核心功能
- `POST /chat` - 與 Agent 對話
- `GET /tools` - 列出可用工具
- `GET /conversations/{thread_id}` - 查看對話歷史
- `DELETE /conversations/{thread_id}` - 清除對話

### API 文檔
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 💻 使用範例

### 範例 1：本地測試（單機模式）

```bash
# 啟動
./start.sh

# 對話
💬 你: 列出當前目錄的 Python 檔案
🤖 Agent: [自動執行並回答]
```

### 範例 2：遠端使用（Server/Client）

**Server 機器:**
```bash
./sh/server.sh
# Server 監聽 0.0.0.0:8000
```

**Client 機器:**
```bash
# 連接遠端 Server
./sh/client.sh http://192.168.1.100:8000

# 或設定環境變數
export AGENT_SERVER_URL=http://192.168.1.100:8000
./sh/client.sh
```

### 範例 3：API 呼叫

```bash
# 健康檢查
curl http://localhost:8000/health

# 對話
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "列出當前目錄的檔案",
    "thread_id": "my-session"
  }'

# 查看工具
curl http://localhost:8000/tools

# 查看狀態
curl http://localhost:8000/status
```

## 🔧 Client 指令

在 Client 中可使用：

```
/help     - 顯示幫助訊息
/status   - 顯示 Server 狀態（工具數、活躍對話數）
/tools    - 列出所有可用工具（filesystem 等）
/history  - 顯示當前對話歷史
/clear    - 清除對話記憶，開始新對話
/exit     - 離開 Client
```

## 🐛 常見問題

### Q: Server 啟動失敗
```bash
# 檢查 LM Studio
curl http://localhost:1234/v1/models

# 檢查 port 8000
lsof -i :8000
```

### Q: Client 無法連接
```bash
# 測試 Server
curl http://localhost:8000/health

# 檢查 URL 是否正確
./sh/client.sh http://localhost:8000
```

### Q: 想同時執行多個 Client
```bash
# 終端機 1
./sh/client.sh

# 終端機 2（另一個客戶端）
./sh/client.sh

# 終端機 3（遠端連接）
./sh/client.sh http://server-ip:8000
```

## 📊 運行流程圖

### 單機模式
```
使用者
  ↓
./start.sh
  ↓
chat_client.py
  ↓
agent.py (ReAct Agent)
  ↓
MCP Tools
  ↓
LM Studio
```

### Server/Client 模式
```
使用者                     Server 機器
  ↓                           ↓
./sh/client.sh         ./sh/server.sh
  ↓                           ↓
client_remote.py          server.py (FastAPI)
  ↓                           ↓
  └─── HTTP API ────────→ agent.py (ReAct Agent)
                              ↓
                         MCP Tools
                              ↓
                         LM Studio
```

## 🎓 學習建議

1. **初學者** - 先用單機模式熟悉 Agentic AI 行為
   ```bash
   ./start.sh
   ```

2. **進階使用** - 理解 Server/Client 架構
   ```bash
   # 終端機 1
   ./sh/server.sh

   # 終端機 2
   ./sh/client.sh
   ```

3. **API 開發** - 查看 Swagger 文檔，整合到自己的應用
   ```bash
   open http://localhost:8000/docs
   ```

## 🚀 下一步

- ✅ 已完成：基礎 Server/Client 架構
- 🔄 可擴充：加入 bash、ripgrep MCP servers
- 📈 可優化：增加認證、限流、快取
- 🎨 可美化：建立 Web UI（Streamlit/Gradio）

---

**GitHub**: https://github.com/bohachu/langgraph-local

有問題請參考：
- [SERVER_CLIENT_GUIDE.md](SERVER_CLIENT_GUIDE.md) - 詳細指南
- [README.md](README.md) - 專案說明
- [QUICKSTART.md](QUICKSTART.md) - 快速開始
