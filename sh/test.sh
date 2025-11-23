#!/bin/bash

# 測試 Server/Client 功能

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🧪 測試 LangGraph Server/Client"
echo "================================"
echo ""

cd "$PROJECT_DIR"

# 測試 Server 健康檢查
echo "1️⃣  測試 Server 健康檢查..."
if curl -s http://localhost:8011/health > /dev/null 2>&1; then
    echo "   ✅ Server 運行中"

    # 顯示狀態
    echo ""
    echo "2️⃣  Server 狀態:"
    curl -s http://localhost:8011/status | python3 -m json.tool

    # 列出工具
    echo ""
    echo "3️⃣  可用工具:"
    curl -s http://localhost:8011/tools | python3 -m json.tool

    # 測試對話
    echo ""
    echo "4️⃣  測試對話功能..."
    response=$(curl -s -X POST http://localhost:8011/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "hello", "thread_id": "test"}')

    echo "   回應:"
    echo "$response" | python3 -m json.tool

    echo ""
    echo "✅ 所有測試通過！"

else
    echo "   ❌ Server 未運行"
    echo ""
    echo "請先啟動 Server:"
    echo "   ./sh/server.sh"
    exit 1
fi

echo ""
echo "================================"
echo "測試完成"
