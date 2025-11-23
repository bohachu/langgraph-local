# 🌐 Server/Client 分離架構使用指南

## 📖 架構說明

專案現在支援兩種運行模式：

### 1️⃣ 單機模式（原有）
- 一個程序同時包含 Agent 和 Client
- 適合：快速測試、單機使用
- 啟動：`./start.sh` 或 `python3 chat_client.py`

### 2️⃣ Server/Client 分離模式（新增）
- Server 和 Client 分開運行
- 適合：遠端存取、多客戶端、生產環境
- 啟動：分別執行 `./sh/server.sh` 和 `./sh/client.sh`

## 🏗️ Server/Client 架構

```
┌─────────────────────┐         HTTP API         ┌─────────────────────┐
│                     │  ←─────────────────────→  │                     │
│  Client             │   POST /chat             │  Server             │
│  (client_remote.py) │   GET /status            │  (server.py)        │
│                     │   GET /tools             │                     │
│  - Terminal UI      │                          │  - FastAPI          │
│  - 指令處理         │                          │  - ReAct Agent      │
│  - HTTP 請求        │                          │  - MCP Tools        │
│                     │                          │  - LM Studio        │
└─────────────────────┘                          └─────────────────────┘
                                                           ↓
                                                  ┌─────────────────────┐
                                                  │  LM Studio          │
                                                  │  (localhost:1234)   │
                                                  └─────────────────────┘
```

## 🚀 快速開始

### 方式一：同一台機器測試

**終端機 1 - 啟動 Server:**
```bash
cd /Users/40gpu/coding_projects/langgraph-local
./sh/server.sh
```

等待看到：
```
✅ Agent Server 已就緒
📡 監聽位址: http://0.0.0.0:8000
```

**終端機 2 - 啟動 Client:**
```bash
cd /Users/40gpu/coding_projects/langgraph-local
./sh/client.sh
```

### 方式二：遠端連接

**Server 機器:**
```bash
./sh/server.sh
# Server 會監聽 0.0.0.0:8000（可從外部連接）
```

**Client 機器:**
```bash
# 指定 Server 位址
./sh/client.sh http://192.168.1.100:8000

# 或設定環境變數
export AGENT_SERVER_URL=http://192.168.1.100:8000
./sh/client.sh
```

## 📡 API 端點

Server 提供以下 HTTP API：

### 基本端點

- `GET /` - 服務資訊
- `GET /health` - 健康檢查
- `GET /status` - 伺服器狀態（工具數、活躍對話數）

### 核心功能

- `POST /chat` - 與 Agent 對話
  ```json
  {
    "message": "列出當前目錄的檔案",
    "thread_id": "optional-thread-id",
    "verbose": false
  }
  ```

- `GET /tools` - 列出所有可用工具

- `GET /conversations/{thread_id}` - 取得對話歷史

- `DELETE /conversations/{thread_id}` - 清除對話

### API 文檔

啟動 Server 後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎮 Client 使用

### 互動式指令

在 Client 中可使用：

```
/help     - 顯示幫助訊息
/status   - 顯示 Server 狀態
/tools    - 列出所有可用工具
/history  - 顯示對話歷史
/clear    - 清除對話記憶
/exit     - 離開 Client
```

### 使用範例

```
💬 你: 列出當前目錄的所有 Python 檔案

🤖 Agent 處理中...

🤖 Agent:
當前目錄包含以下 Python 檔案:
1. agent.py - ReAct Agent 核心實作
2. server.py - FastAPI 伺服器
3. client_remote.py - 遠端客戶端
4. chat_client.py - 本地客戶端

📊 對話訊息數: 1
```

## 🔧 進階配置

### Server 配置

編輯 `server.py` 修改：

```python
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",      # 監聽位址
        port=8000,           # 監聽 port
        reload=False,        # 開發模式熱重載
        log_level="info"     # 日誌級別
    )
```

### 環境變數

```bash
# Server URL（Client 使用）
export AGENT_SERVER_URL=http://localhost:8000

# LM Studio URL（Server 使用）
export LM_STUDIO_URL=http://localhost:1234/v1

# 模型名稱
export MODEL_NAME=gemma-3n-e4b-it-mlx
```

## 🐛 故障排除

### 問題：Server 啟動失敗

**症狀：**
```
❌ 初始化失敗: Connection refused
```

**解決方法：**
1. 確認 LM Studio 已啟動並載入模型
2. 確認 API Server 運行於 localhost:1234
3. 測試連線：`curl http://localhost:1234/v1/models`

### 問題：Client 無法連接

**症狀：**
```
❌ 無法連接伺服器: Connection refused
```

**解決方法：**
1. 確認 Server 已啟動
2. 測試連線：`curl http://localhost:8000/health`
3. 檢查防火牆設定
4. 確認 URL 正確（包含 http:// 前綴）

### 問題：Port 8000 已被使用

**解決方法：**
```bash
# 查看哪個程序使用 port 8000
lsof -i :8000

# 關閉該程序（謹慎使用）
lsof -ti:8000 | xargs kill -9

# 或修改 server.py 使用其他 port
```

### 問題：MCP 工具無法使用

**症狀：**
```
❌ MCP filesystem server 無法啟動
```

**解決方法：**
1. 確認 Node.js 已安裝：`node --version`
2. 測試 MCP server：`npx -y @modelcontextprotocol/server-filesystem .`
3. 檢查路徑權限

## 🔐 安全性考量

### 生產環境建議

1. **使用 HTTPS**
   ```python
   # 使用 SSL 憑證
   uvicorn.run(
       "server:app",
       host="0.0.0.0",
       port=8000,
       ssl_keyfile="/path/to/key.pem",
       ssl_certfile="/path/to/cert.pem"
   )
   ```

2. **加入認證**
   - 使用 FastAPI 的 OAuth2 或 API Key
   - 限制允許的客戶端 IP

3. **限制檔案系統存取**
   - MCP filesystem server 只開放特定目錄
   - 不要使用 root 權限運行

4. **設定 CORS**
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://trusted-domain.com"],
       allow_methods=["POST", "GET"],
   )
   ```

## 📊 效能優化

### Server 端

1. **增加 Worker 數量**
   ```bash
   uvicorn server:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. **啟用快取**
   - 快取常用的 Agent 回應
   - 使用 Redis 或 Memcached

3. **限流**
   ```python
   from slowapi import Limiter

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter

   @app.post("/chat")
   @limiter.limit("10/minute")
   async def chat(request: ChatRequest):
       ...
   ```

### Client 端

1. **連線池**
   - 重用 HTTP 連線
   - 設定適當的 timeout

2. **非同步請求**
   - 使用 `httpx.AsyncClient` 處理多個請求

## 🌍 部署選項

### Docker 部署

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "server.py"]
```

**執行：**
```bash
docker build -t langgraph-agent .
docker run -p 8000:8000 langgraph-agent
```

### 雲端部署

- **Heroku**: `Procfile` + `requirements.txt`
- **AWS EC2**: 使用 systemd 或 supervisor
- **Google Cloud Run**: 容器化部署
- **Railway/Render**: 一鍵部署

## 🔄 與單機模式的差異

| 特性 | 單機模式 | Server/Client 模式 |
|------|---------|------------------|
| **架構** | All-in-one | 分離式 |
| **多客戶端** | ❌ | ✅ |
| **遠端存取** | ❌ | ✅ |
| **水平擴展** | ❌ | ✅ |
| **複雜度** | 低 | 中 |
| **適合場景** | 個人使用 | 團隊/生產 |

## 📝 總結

選擇建議：
- **快速測試** → 使用 `./start.sh`（單機模式）
- **團隊協作** → 使用 `./sh/server.sh` + `./sh/client.sh`
- **生產部署** → Server/Client 模式 + Docker

享受你的 Agentic AI Server！🎉
