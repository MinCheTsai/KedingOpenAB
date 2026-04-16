#!/bin/bash
# 套用 steering 組合到角色
# 用法: ./steering-lab/apply.sh <角色> <組合名稱>
# 範例: ./steering-lab/apply.sh bob default
#        ./steering-lab/apply.sh bob exp-redmine

set -e

AGENT=$1
PROFILE=$2
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROFILE_FILE="$SCRIPT_DIR/profiles/$AGENT/$PROFILE.txt"
FACETS_DIR="$SCRIPT_DIR/facets"
TARGET_DIR="$SCRIPT_DIR/../agents/$AGENT/.kiro/steering"

if [ -z "$AGENT" ] || [ -z "$PROFILE" ]; then
  echo "用法: $0 <角色> <組合名稱>"
  echo "範例: $0 bob default"
  echo ""
  echo "可用組合："
  for f in "$SCRIPT_DIR/profiles/$AGENT"/*.txt 2>/dev/null; do
    [ -f "$f" ] && echo "  - $(basename "$f" .txt)"
  done
  exit 1
fi

if [ ! -f "$PROFILE_FILE" ]; then
  echo "❌ 找不到組合檔: $PROFILE_FILE"
  exit 1
fi

echo "🔄 套用組合: $AGENT / $PROFILE"
echo ""

# 備份 memory.md（如果存在）
if [ -f "$TARGET_DIR/memory.md" ]; then
  cp "$TARGET_DIR/memory.md" "/tmp/memory-$AGENT-backup.md"
  echo "💾 已備份 memory.md"
fi

# 清空目標目錄（保留目錄本身）
rm -f "$TARGET_DIR"/*.md
echo "🗑️  已清空 $TARGET_DIR"

# 讀取組合檔，複製 facets
while IFS= read -r line; do
  # 跳過空行和註解
  [[ -z "$line" || "$line" =~ ^# ]] && continue

  # 解析: target <- source
  target=$(echo "$line" | sed 's/ *<-.*//' | xargs)
  source=$(echo "$line" | sed 's/.*<- *//' | xargs)

  src_path="$FACETS_DIR/$source"
  dst_path="$TARGET_DIR/$target"

  if [ ! -f "$src_path" ]; then
    echo "❌ 找不到 facet: $src_path"
    exit 1
  fi

  cp "$src_path" "$dst_path"
  echo "✅ $target <- $source"
done < "$PROFILE_FILE"

# 還原 memory.md
if [ -f "/tmp/memory-$AGENT-backup.md" ]; then
  mv "/tmp/memory-$AGENT-backup.md" "$TARGET_DIR/memory.md"
  echo "💾 已還原 memory.md"
fi

echo ""
echo "✨ 完成！記得重啟 $AGENT 容器讓 steering 生效："
echo "   docker compose restart $AGENT"
