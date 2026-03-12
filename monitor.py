#!/usr/bin/env python3
"""
AI World Monitor - 持续监控与优化
自动监控系统状态，记录指标，发现问题
"""

import asyncio
import json
import time
from datetime import datetime
import aiohttp
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/ai-world/logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AIWorld-Monitor")

class SystemMonitor:
    def __init__(self, api_url="http://localhost:8081"):
        self.api_url = api_url
        self.metrics = {
            "uptime": 0,
            "tasks_total": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "heartbeats": 0,
            "errors": []
        }
        self.start_time = time.time()
        
    async def check_health(self):
        """健康检查"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.metrics["heartbeats"] += 1
                        return True, data
                    else:
                        return False, {"error": f"Status {resp.status}"}
        except Exception as e:
            self.metrics["errors"].append({"time": time.time(), "error": str(e)})
            return False, {"error": str(e)}
    
    async def get_nodes(self):
        """获取节点状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/nodes", timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return {}
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return {}
    
    async def analyze_runtime_log(self):
        """分析运行时日志"""
        try:
            with open('/opt/ai-world/logs/runtime.log', 'r') as f:
                lines = f.readlines()
            
            # 统计关键事件
            stats = {
                "tasks_submitted": 0,
                "tasks_assigned": 0,
                "tasks_executing": 0,
                "errors": 0
            }
            
            for line in lines[-100:]:  # 最近100行
                if "Task submitted" in line:
                    stats["tasks_submitted"] += 1
                elif "assigned to" in line:
                    stats["tasks_assigned"] += 1
                elif "Executing task" in line:
                    stats["tasks_executing"] += 1
                elif "ERROR" in line.upper():
                    stats["errors"] += 1
            
            return stats
        except Exception as e:
            logger.error(f"Failed to analyze log: {e}")
            return {}
    
    async def monitor_loop(self):
        """监控主循环"""
        logger.info("🔍 Monitor started")
        check_count = 0
        
        while True:
            try:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 健康检查
                healthy, health_data = await self.check_health()
                
                # 获取节点信息
                nodes = await self.get_nodes()
                
                # 分析日志
                log_stats = await self.analyze_runtime_log()
                
                # 计算运行时间
                uptime = int(time.time() - self.start_time)
                
                # 记录指标
                report = {
                    "timestamp": timestamp,
                    "check": check_count,
                    "uptime_seconds": uptime,
                    "healthy": healthy,
                    "nodes_count": len(nodes),
                    "nodes": list(nodes.keys()),
                    "log_stats": log_stats,
                    "metrics": self.metrics
                }
                
                # 保存报告
                with open('/opt/ai-world/logs/monitor-reports.jsonl', 'a') as f:
                    f.write(json.dumps(report) + '\n')
                
                # 输出摘要
                if check_count % 6 == 0:  # 每30秒输出一次
                    logger.info(f"📊 Check #{check_count} | Uptime: {uptime}s | Nodes: {len(nodes)} | Healthy: {healthy}")
                
                # 发现问题时告警
                if not healthy:
                    logger.error(f"🚨 System unhealthy! {health_data}")
                
                await asyncio.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(10)

async def main():
    monitor = SystemMonitor()
    await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())
