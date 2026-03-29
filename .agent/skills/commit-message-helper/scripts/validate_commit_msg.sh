#!/bin/bash

# 取得輸入參數 (對應 sys.argv[1])
MESSAGE="$1"

# 如果沒有參數，設為空字串
if [ -z "$MESSAGE" ]; then
    MESSAGE=""
fi

# 取出第一行 (對應 message.split('\n')[0])
FIRST_LINE=$(echo "$MESSAGE" | head -n 1)

# 定義正規表達式 (與 Python 版本相同)
# 注意：在 Bash 中，括號 () 不需要跳脫，但為了與變數配合，我們用引號包起來
PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,50}"

# 進行比對
if [[ "$FIRST_LINE" =~ $PATTERN ]]; then
    echo "Valid commit message format"
    exit 0
else
    echo "Invalid format. Expected: type(scope): subject"
    exit 1
fi
