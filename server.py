#!/usr/bin/env python3
"""
FastAPI Server for LangGraph ReAct Agent
提供 HTTP API 介面，讓 client 可以遠端呼叫 Agentic AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import json
from agent import AgenticChatBot
from contextlib import asynccontextmanager

# 全域 agent 實例
agent: Optional[AgenticChatBot] = None

# 儲存多個對話執行緒
conversations: Dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    global agent

    print("🚀 啟動 LangGraph Agent Server...")
    print("="*60)

    # 初始化 Agent
    try:
        agent = AgenticChatBot()
        print("\n✅ Agent Server 已就緒")
        print(f"📡 監聽位址: http://0.0.0.0:8011")
        print(f"📚 API 文檔: http://localhost:8011/docs")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        raise

    yield

    # 清理資源
    print("\n👋 關閉 Agent Server...")


app = FastAPI(
    title="LangGraph Agentic AI Server",
    description="類似 Claude Code 的自主執行 AI Agent API",
    version="1.0.0",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    """對話請求"""
    message: str
    thread_id: Optional[str] = "default"
    verbose: bool = False


class ChatResponse(BaseModel):
    """對話回應"""
    response: str
    thread_id: str
    message_count: int


class StatusResponse(BaseModel):
    """狀態回應"""
    status: str
    tools_count: int
    active_threads: int


@app.get("/")
async def root():
    """根路徑"""
    return {
        "service": "LangGraph Agentic AI Server",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康檢查"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {
        "status": "healthy",
        "agent": "ready",
        "tools": len(agent.tools)
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """取得伺服器狀態"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return StatusResponse(
        status="running",
        tools_count=len(agent.tools),
        active_threads=len(conversations)
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    與 Agentic AI 對話

    Agent 會自主執行多步驟來完成使用者的意圖
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # 執行 Agent（自主多步驟執行）
        response = agent.chat(
            user_message=request.message,
            thread_id=request.thread_id
        )

        # 記錄對話歷史
        if request.thread_id not in conversations:
            conversations[request.thread_id] = []

        conversations[request.thread_id].append({
            "user": request.message,
            "assistant": response
        })

        return ChatResponse(
            response=response,
            thread_id=request.thread_id,
            message_count=len(conversations[request.thread_id])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/conversations/{thread_id}")
async def get_conversation(thread_id: str):
    """取得特定對話執行緒的歷史"""
    if thread_id not in conversations:
        raise HTTPException(status_code=404, detail="Thread not found")

    return {
        "thread_id": thread_id,
        "messages": conversations[thread_id],
        "count": len(conversations[thread_id])
    }


@app.delete("/conversations/{thread_id}")
async def clear_conversation(thread_id: str):
    """清除特定對話執行緒"""
    if thread_id in conversations:
        del conversations[thread_id]
        return {"status": "cleared", "thread_id": thread_id}
    else:
        raise HTTPException(status_code=404, detail="Thread not found")


@app.get("/tools")
async def list_tools():
    """列出所有可用的工具"""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    tools_info = []
    for tool in agent.tools:
        tools_info.append({
            "name": tool.name,
            "description": tool.description[:100] if tool.description else "No description"
        })

    return {
        "count": len(tools_info),
        "tools": tools_info
    }


if __name__ == "__main__":
    # 直接執行時啟動伺服器
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8011,
        reload=False,  # 生產環境關閉 reload
        log_level="info"
    )
