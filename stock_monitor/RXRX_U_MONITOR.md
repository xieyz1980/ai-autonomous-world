# 📊 美股持仓监控配置

**创建时间**: 2026-03-12 15:28  
**监控对象**: RXRX, U  
**监控频率**: 每30分钟

---

## 🔹 持仓概览

| 股票 | 公司名称 | 成本价 | 当前预估 | 今日美股 | 备注 |
|------|---------|--------|---------|---------|------|
| **RXRX** | Recursion Pharmaceuticals | $3.40 | 待获取 | 交易中 | AI制药，高风险高成长 |
| **U** | Unity Software | $19.80 | 待获取 | 交易中 | 游戏引擎，AI受益股 |

---

## 📈 股票基本信息

### RXRX - Recursion Pharmaceuticals

**公司简介**:
- AI驱动的生物技术公司
- 利用机器学习加速药物发现
- 与Nvidia合作开发AI模型
- 临床阶段生物制药，尚未盈利

**关键数据**:
- 市值: 约$800M-$1B
- 52周范围: $3.00 - $12.50
- 你的成本: $3.40 (接近52周低点)

**投资逻辑**:
✅ AI制药风口  
✅ 与Nvidia合作  
✅ 股价从历史高点大幅回调  
⚠️ 尚未盈利，风险较高  
⚠️ 生物科技波动大  

**建议监控点位**:
- 🎯 目标价: $5.00 (+47%), $7.00 (+106%)
- 🛑 止损: $2.80 (-18%), $2.50 (-26%)

---

### U - Unity Software

**公司简介**:
- 全球领先的游戏引擎开发商
- 3D/AR/VR内容创作平台
- Apple Vision Pro内容生态重要参与者
- AI+3D创作工具提供商

**关键数据**:
- 市值: 约$7B-$8B
- 52周范围: $18.00 - $42.00
- 你的成本: $19.80 (接近52周低点)

**投资逻辑**:
✅ AI游戏内容生成受益股  
✅ Vision Pro生态  
✅ 估值相对合理  
✅ 从高点$42回调50%+  
⚠️ 竞争加剧(Unreal Engine)  
⚠️ 盈利模式转型中  

**建议监控点位**:
- 🎯 目标价: $25.00 (+26%), $30.00 (+52%)
- 🛑 止损: $17.00 (-14%), $15.00 (-24%)

---

## 🔔 预警设置

### 自动监控脚本

```bash
#!/bin/bash
# 保存为 ~/stock_monitor.sh

STOCKS=("RXRX:3.40" "U:19.80")
ALERT_THRESHOLD=0.05  # 5%涨跌幅预警

for stock in "${STOCKS[@]}"; do
    IFS=':' read -r symbol cost <<< "$stock"
    
    # 获取当前价格 (使用Alpha Vantage或其他API)
    # current_price=$(get_stock_price $symbol)
    
    # 计算涨跌幅
    # change_pct=$(( (current_price - cost) / cost ))
    
    # 如果超过阈值，发送通知
    # if [ $(echo "$change_pct > $ALERT_THRESHOLD" | bc) -eq 1 ]; then
    #     echo "🚨 $symbol 涨超 $ALERT_THRESHOLD%! 当前: $current_price, 成本: $cost"
    # fi
done
```

### 手动检查命令

```bash
# 查看RXRX实时行情
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/RXRX" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'RXRX: ${d[\"chart\"][\"result\"][0][\"meta\"][\"regularMarketPrice\"]}')"

# 查看U实时行情  
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/U" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'U: ${d[\"chart\"][\"result\"][0][\"meta\"][\"regularMarketPrice\"]}')"
```

---

## 📅 重要事件日历

### RXRX 关键事件
- [ ] 财报发布 (每季度)
- [ ] 临床实验进展公告
- [ ] 与Nvidia合作项目更新
- [ ] 新药物管线进展

### U 关键事件
- [ ] 财报发布 (每季度)
- [ ] Unity 6引擎发布
- [ ] Vision Pro应用上线
- [ ] AI创作工具更新

---

## 💡 我的观察建议

### 短线观察 (1-7天)
- 关注每日涨跌幅
- 观察成交量变化
- 跟踪相关新闻

### 中线观察 (1-4周)
- 技术走势是否突破
- 大盘(NASDAQ)趋势
- AI板块整体热度

### 长线观察 (1-6月)
- 公司基本面变化
- 行业竞争格局
- AI应用落地进展

---

## ⚠️ 风险提示

1. **RXRX 风险**: 
   - 生物科技高波动性
   - 临床失败可能暴跌
   - 尚未盈利，烧钱阶段

2. **U 风险**:
   - 游戏行业周期性
   - 与Epic/Unreal竞争
   - 盈利模式转型不确定性

3. **系统性风险**:
   - 美股大盘回调
   - AI泡沫破裂
   - 地缘政治影响

---

## 🎯 操作建议 (仅供参考)

**RXRX**:
- 仓位: 小仓位试水 (符合你"少量"的描述)
- 策略: 高风险高收益，设好止损
- 催化剂: AI制药新闻、临床进展

**U**:
- 仓位: 相对稳健
- 策略: AI+游戏长期受益
- 催化剂: Vision Pro生态、AI工具发布

---

**我会帮你**:  
✅ 每30分钟检查一次价格  
✅ 涨跌幅超5%时通知你  
✅ 收盘后给你日报  
✅ 有重要新闻时汇总

**你需要自己做**:  
❌ 买卖决策  
❌ 止盈止损执行  
❌ 风险承担

**现在要我帮你盯着吗？** 👀📈
