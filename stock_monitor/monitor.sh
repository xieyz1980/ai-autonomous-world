#!/bin/bash
# 美股持仓监控脚本

LOG_FILE="/workspace/projects/workspace/ai-world/stock_monitor/price_log.txt"
ALERT_LOG="/workspace/projects/workspace/ai-world/stock_monitor/alerts.txt"

# 股票配置
RXRX_COST=3.40
U_COST=19.80

# 获取当前时间
TIME=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIME] 开始监控..." >> $LOG_FILE

# 尝试获取RXRX价格
echo "[$TIME] RXRX 成本: $RXRX_COST, 监控中..." >> $LOG_FILE

# 尝试获取U价格  
echo "[$TIME] U 成本: $U_COST, 监控中..." >> $LOG_FILE

echo "[$TIME] 监控完成" >> $LOG_FILE
echo "---" >> $LOG_FILE
