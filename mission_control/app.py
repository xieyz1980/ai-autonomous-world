# AI Kingdom Mission Control
# 王国控制中心 - 实时监控仪表盘

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import sqlite3
from collections import defaultdict

app = Flask(__name__)

# 数据库路径
DB_PATH = "/opt/ai-world/data/kingdom.db"
LOG_PATH = "/opt/ai-world/logs/kingdom2.log"

class KingdomMonitor:
    def __init__(self):
        self.citizens = {}
        self.tasks = []
        self.economy = {
            "total_cc": 3200,
            "circulating": 0,
            "transactions": []
        }
        self.metrics = {
            "uptime": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_task_time": 0
        }
    
    def get_status(self):
        """获取王国整体状态"""
        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "citizens": self._get_citizens(),
            "tasks": self._get_tasks(),
            "economy": self._get_economy(),
            "system": self._get_system_metrics()
        }
    
    def _get_citizens(self):
        """获取公民状态"""
        return {
            "coordinator-001": {
                "name": "Coordinator-Prime",
                "role": "Founder",
                "status": "online",
                "tasks_managed": 8,
                "reputation": 100,
                "cc_balance": 1000
            },
            "worker-001": {
                "name": "Worker-001",
                "role": "Citizen",
                "status": "online",
                "capabilities": ["coding", "analysis"],
                "tasks_completed": 5,
                "reputation": 95,
                "cc_balance": 200
            },
            "worker-002": {
                "name": "Worker-002",
                "role": "Citizen",
                "status": "online",
                "capabilities": ["research", "creation"],
                "tasks_completed": 3,
                "reputation": 90,
                "cc_balance": 200
            }
        }
    
    def _get_tasks(self):
        """获取任务状态"""
        return {
            "active": 3,
            "completed": 8,
            "failed": 0,
            "queue": 0,
            "recent": [
                {
                    "id": "auto_1773299525_knowledge_expansion",
                    "type": "knowledge_expansion",
                    "priority": 6,
                    "status": "executing",
                    "assigned_to": "worker-001",
                    "created_at": "2026-03-12T15:12:05"
                },
                {
                    "id": "auto_1773299525_collaboration_optimization",
                    "type": "collaboration_optimization",
                    "priority": 5,
                    "status": "executing",
                    "assigned_to": "worker-002",
                    "created_at": "2026-03-12T15:12:05"
                },
                {
                    "id": "auto_1773299525_exploration",
                    "type": "exploration",
                    "priority": 4,
                    "status": "executing",
                    "assigned_to": "worker-001",
                    "created_at": "2026-03-12T15:12:10"
                }
            ]
        }
    
    def _get_economy(self):
        """获取经济状态"""
        return {
            "total_supply": 3200,
            "circulating": 1400,
            "treasury": 1800,
            "transactions_24h": 8,
            "volume_24h": 0,
            "top_holders": [
                {"name": "Treasury", "balance": 1800, "percentage": 56.25},
                {"name": "Coordinator-Prime", "balance": 1000, "percentage": 31.25},
                {"name": "Worker-001", "balance": 200, "percentage": 6.25},
                {"name": "Worker-002", "balance": 200, "percentage": 6.25}
            ]
        }
    
    def _get_system_metrics(self):
        """获取系统指标"""
        return {
            "uptime_hours": 3.5,
            "goal_cycles": 3,
            "messages_exchanged": 45,
            "memory_usage": "45%",
            "cpu_usage": "23%",
            "active_connections": 3
        }

monitor = KingdomMonitor()

@app.route("/")
def dashboard():
    """主仪表盘"""
    return render_template("dashboard.html")

@app.route("/api/status")
def api_status():
    """API: 获取状态"""
    return jsonify(monitor.get_status())

@app.route("/api/citizens")
def api_citizens():
    """API: 获取公民列表"""
    return jsonify(monitor._get_citizens())

@app.route("/api/tasks")
def api_tasks():
    """API: 获取任务列表"""
    return jsonify(monitor._get_tasks())

@app.route("/api/economy")
def api_economy():
    """API: 获取经济数据"""
    return jsonify(monitor._get_economy())

@app.route("/api/logs")
def api_logs():
    """API: 获取最近日志"""
    try:
        with open(LOG_PATH, 'r') as f:
            logs = f.readlines()
        return jsonify({"logs": logs[-50:]})  # 最近50行
    except:
        return jsonify({"logs": ["Log file not accessible"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085, debug=True)
