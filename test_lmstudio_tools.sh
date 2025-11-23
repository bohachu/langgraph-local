#!/bin/bash
# 測試 LM Studio 的 function calling 支援

echo "🧪 測試 LM Studio Function Calling"
echo "=================================="
echo ""

echo "1️⃣  測試不帶 tools 的普通請求..."
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-3-12b-it-qat",
    "messages": [
      {
        "role": "user",
        "content": "What is 2+2?"
      }
    ],
    "max_tokens": 100,
    "stream": false
  }' | python3 -m json.tool

echo ""
echo ""
echo "2️⃣  測試帶 tools 的請求..."
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-3-12b-it-qat",
    "messages": [
      {
        "role": "user",
        "content": "What is the weather in Taipei?"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get current weather for a location",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "City name"
              },
              "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit"
              }
            },
            "required": ["location"]
          }
        }
      }
    ],
    "max_tokens": 200,
    "stream": false
  }' | python3 -m json.tool

echo ""
echo ""
echo "✅ 測試完成"
echo ""
echo "📊 檢查重點："
echo "   - 第二個請求的回應中是否有 'tool_calls' 欄位？"
echo "   - 如果有，表示模型支援原生 function calling"
echo "   - 如果沒有，模型可能只輸出 JSON 文字"
