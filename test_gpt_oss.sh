#!/bin/bash
# 測試 gpt-oss-20b 的工具調用能力

echo "🧪 測試 gpt-oss-20b + LangGraph + MCP 工具調用"
echo "=============================================="
echo ""

echo "📝 測試請求：列出當前目錄的 Python 檔案"
echo ""

curl -X POST http://localhost:8011/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "請列出當前目錄有哪些 Python 檔案？",
    "thread_id": "test_gpt_oss"
  }' \
  -s | python3 -m json.tool

echo ""
echo "✅ 測試完成"
echo ""
echo "📊 檢查重點："
echo "   1. 回應中是否包含實際的檔案列表？"
echo "   2. 是否有 .py 檔案？（agent.py, server.py 等）"
echo "   3. 是否有工具調用的軌跡？"
