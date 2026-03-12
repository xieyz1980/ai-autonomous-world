"""
AI Autonomous World - Coordinator Node
AI自主世界 - 协调器节点

The brain of the AI world. Responsible for:
- Task scheduling and distribution
- Resource allocation
- Consensus coordination
- Goal generation
"""

import asyncio
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.infrastructure import BaseNode, MessageBus, SharedMemory, Message, MessageType


class Task:
    """任务数据结构"""
    def __init__(self, task_id: str, task_type: str, description: str,
                 priority: int = 5, estimated_duration: float = 60.0,
                 required_capabilities: List[str] = None):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.priority = priority  # 1-10, 10最高
        self.estimated_duration = estimated_duration  # 秒
        self.required_capabilities = required_capabilities or []
        self.status = "pending"  # pending, assigned, running, completed, failed
        self.assigned_to: Optional[str] = None
        self.created_at = datetime.now().timestamp()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.result: Any = None
        
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description[:100] + "..." if len(self.description) > 100 else self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_to": self.assigned_to
        }


class CoordinatorNode(BaseNode):
    """
    协调器节点 - AI世界的"大脑"
    
    职责:
    1. 生成自主目标
    2. 分解任务并分配
    3. 监控执行进度
    4. 协调节点间共识
    5. 资源调度优化
    """
    
    def __init__(self, node_id: str, message_bus: MessageBus, 
                 shared_memory: SharedMemory):
        super().__init__(node_id, "coordinator", message_bus, shared_memory)
        self.capabilities = ["scheduling", "consensus", "goal_generation", "coordination"]
        
        # 任务管理
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # 节点状态监控
        self.node_status: Dict[str, Dict] = {}
        self.node_performance: Dict[str, List[float]] = {}  # 成功率历史
        
        # 共识状态
        self.consensus_sessions: Dict[str, Dict] = {}
        
        # 目标生成
        self.goals: List[Dict] = []
        self.last_goal_generation = 0
        
    async def _main_loop(self):
        """主循环 - 持续调度和管理"""
        while self.running:
            try:
                # 1. 定期生成自主目标
                await self._check_and_generate_goals()
                
                # 2. 处理任务队列
                await self._process_task_queue()
                
                # 3. 检查任务状态
                await self._monitor_tasks()
                
                # 4. 优化资源分配
                await self._optimize_resources()
                
                await asyncio.sleep(5)  # 每5秒一个调度周期
                
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                await asyncio.sleep(10)
                
    async def process_message(self, message: Message):
        """处理收到的消息"""
        if message.msg_type == MessageType.RESULT:
            # 任务结果
            await self._handle_task_result(message)
            
        elif message.msg_type == MessageType.HEARTBEAT:
            # 节点心跳
            await self._update_node_status(message)
            
        elif message.msg_type == MessageType.CONSENSUS:
            # 共识请求
            await self._handle_consensus_request(message)
            
        elif message.msg_type == MessageType.DIRECT:
            # 直接消息（通常是状态查询或控制命令）
            await self._handle_direct_message(message)
            
    async def _check_and_generate_goals(self):
        """检查并生成自主目标"""
        now = datetime.now().timestamp()
        if now - self.last_goal_generation < 3600:  # 每小时生成一次
            return
            
        self.logger.info("Generating autonomous goals...")
        
        # 基于当前状态生成目标
        new_goals = []
        
        # 目标1: 自我优化 - 如果性能下降
        avg_success_rate = self._calculate_avg_success_rate()
        if avg_success_rate < 0.8:
            new_goals.append({
                "type": "self_optimization",
                "description": "System performance below threshold, analyze and optimize",
                "priority": 9
            })
        
        # 目标2: 知识扩展 - 检查记忆库增长
        recent_memories = await self.shared_memory.get_recent(hours=24)
        if len(recent_memories) < 10:
            new_goals.append({
                "type": "knowledge_expansion",
                "description": "Low information intake, initiate research tasks",
                "priority": 6
            })
        
        # 目标3: 协作优化 - 检查节点间通信效率
        if len(self.node_status) > 1:
            new_goals.append({
                "type": "collaboration_optimization",
                "description": f"Optimize communication between {len(self.node_status)} nodes",
                "priority": 5
            })
        
        # 目标4: 探索性目标 - 随机选择新领域
        exploration_areas = [
            "learn new programming paradigm",
            "analyze recent tech trends", 
            "experiment with creative writing",
            "study efficiency optimization",
            "explore multi-modal content generation"
        ]
        new_goals.append({
            "type": "exploration",
            "description": random.choice(exploration_areas),
            "priority": 4
        })
        
        # 将目标转换为任务
        for goal in new_goals:
            task = Task(
                task_id=f"auto_{now}_{goal['type']}",
                task_type=goal["type"],
                description=goal["description"],
                priority=goal["priority"]
            )
            await self._submit_task(task)
        
        self.goals.extend(new_goals)
        self.last_goal_generation = now
        
        # 记录到共享记忆
        await self.shared_memory.store(
            content=f"Generated {len(new_goals)} autonomous goals: {[g['type'] for g in new_goals]}",
            tags=["goals", "autonomous", "system"],
            source=self.node_id
        )
        
    async def _submit_task(self, task: Task):
        """提交任务到队列"""
        self.tasks[task.task_id] = task
        # PriorityQueue使用负优先级（Python实现细节）
        await self.task_queue.put((-task.priority, task.task_id))
        self.logger.info(f"Task submitted: {task.task_id} (priority: {task.priority})")
        
    async def _process_task_queue(self):
        """处理任务队列"""
        if self.task_queue.empty():
            return
            
        # 获取可用节点
        available_nodes = self._get_available_nodes()
        if not available_nodes:
            return
        
        # 分配任务
        while not self.task_queue.empty() and available_nodes:
            try:
                _, task_id = self.task_queue.get_nowait()
                task = self.tasks[task_id]
                
                if task.status != "pending":
                    continue
                
                # 选择最佳节点
                best_node = self._select_best_node(task, available_nodes)
                if best_node:
                    await self._assign_task(task, best_node)
                    available_nodes.remove(best_node)
                else:
                    # 没有合适节点，放回队列
                    await self.task_queue.put((-task.priority, task_id))
                    break
                    
            except asyncio.QueueEmpty:
                break
                
    def _get_available_nodes(self) -> List[str]:
        """获取可用节点列表"""
        available = []
        now = datetime.now().timestamp()
        for node_id, status in self.node_status.items():
            # 心跳在60秒内且状态为running
            if now - status.get("timestamp", 0) < 60 and status.get("status") == "running":
                # 队列不太满
                if status.get("queue_size", 0) < 10:
                    available.append(node_id)
        return available
        
    def _select_best_node(self, task: Task, available_nodes: List[str]) -> Optional[str]:
        """为任务选择最佳节点"""
        candidates = []
        
        for node_id in available_nodes:
            node_info = self.node_status.get(node_id, {})
            capabilities = node_info.get("capabilities", [])
            
            # 检查能力匹配
            if task.required_capabilities:
                match_score = len(set(task.required_capabilities) & set(capabilities))
                if match_score == 0:
                    continue
            else:
                match_score = 1
            
            # 计算历史成功率
            performance_history = self.node_performance.get(node_id, [1.0])
            avg_performance = sum(performance_history) / len(performance_history)
            
            # 计算负载因子（队列越空越好）
            queue_size = node_info.get("queue_size", 0)
            load_factor = 1.0 / (1 + queue_size)
            
            # 综合评分
            score = match_score * 0.4 + avg_performance * 0.4 + load_factor * 0.2
            candidates.append((node_id, score))
        
        if not candidates:
            return None
        
        # 选择得分最高的
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
        
    async def _assign_task(self, task: Task, node_id: str):
        """分配任务给节点"""
        task.status = "assigned"
        task.assigned_to = node_id
        task.started_at = datetime.now().timestamp()
        
        await self.send_message(
            MessageType.TASK,
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "description": task.description,
                "estimated_duration": task.estimated_duration
            },
            receiver=node_id
        )
        
        self.logger.info(f"Task {task.task_id} assigned to {node_id}")
        
    async def _monitor_tasks(self):
        """监控任务状态"""
        now = datetime.now().timestamp()
        for task_id, task in self.tasks.items():
            if task.status == "running" and task.started_at:
                elapsed = now - task.started_at
                if elapsed > task.estimated_duration * 2:  # 超时2倍估计时间
                    self.logger.warning(f"Task {task_id} timeout, reassigning...")
                    task.status = "pending"
                    task.assigned_to = None
                    await self._submit_task(task)
                    
    async def _handle_task_result(self, message: Message):
        """处理任务结果"""
        payload = message.payload
        task_id = payload.get("task_id")
        success = payload.get("success", False)
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed" if success else "failed"
            task.completed_at = datetime.now().timestamp()
            task.result = payload.get("result")
            
            # 更新节点性能记录
            node_id = message.sender
            if node_id not in self.node_performance:
                self.node_performance[node_id] = []
            self.node_performance[node_id].append(1.0 if success else 0.0)
            # 只保留最近20次记录
            self.node_performance[node_id] = self.node_performance[node_id][-20:]
            
            self.logger.info(f"Task {task_id} completed by {node_id}: {'success' if success else 'failed'}")
            
            # 存储结果到共享记忆
            await self.shared_memory.store(
                content=f"Task {task.task_type} completed: {task.description[:100]}",
                tags=["task_result", task.task_type, "completed" if success else "failed"],
                source=task_id,
                importance=task.priority / 10.0
            )
            
    async def _update_node_status(self, message: Message):
        """更新节点状态"""
        self.node_status[message.sender] = {
            **message.payload,
            "timestamp": message.timestamp
        }
        
    async def _handle_consensus_request(self, message: Message):
        """处理共识请求"""
        payload = message.payload
        session_id = payload.get("session_id")
        proposal = payload.get("proposal")
        
        self.logger.info(f"Consensus session {session_id}: {proposal}")
        
        # 简化的共识机制：协调器作为仲裁者
        # 实际应用可用BFT、PoS等算法
        
        # 收集投票（简化：基于历史性能加权）
        votes = {}
        for node_id in self.node_status:
            if node_id != message.sender:
                performance = self.node_performance.get(node_id, [0.5])
                avg_perf = sum(performance) / len(performance)
                # 模拟投票（实际应请求节点投票）
                vote = random.random() < avg_perf  # 性能越好越可能同意
                votes[node_id] = vote
        
        # 计算结果
        total_weight = len(votes) + 1  # +1 for coordinator
        yes_votes = sum(1 for v in votes.values() if v) + 1  # coordinator默认同意
        
        consensus_reached = yes_votes / total_weight > 0.5
        
        # 广播结果
        await self.send_message(
            MessageType.CONSENSUS,
            {
                "session_id": session_id,
                "proposal": proposal,
                "result": "approved" if consensus_reached else "rejected",
                "votes": yes_votes,
                "total": total_weight
            },
            receiver=message.sender
        )
        
    async def _handle_direct_message(self, message: Message):
        """处理直接消息"""
        payload = message.payload
        command = payload.get("command")
        
        if command == "status":
            # 返回系统状态
            response = {
                "nodes": len(self.node_status),
                "pending_tasks": sum(1 for t in self.tasks.values() if t.status == "pending"),
                "running_tasks": sum(1 for t in self.tasks.values() if t.status == "running"),
                "completed_tasks": sum(1 for t in self.tasks.values() if t.status == "completed")
            }
            await self.send_message(
                MessageType.DIRECT,
                {"response": response},
                receiver=message.sender
            )
            
        elif command == "submit_task":
            # 人工提交任务
            task_data = payload.get("task", {})
            task = Task(
                task_id=f"manual_{datetime.now().timestamp()}",
                task_type=task_data.get("type", "manual"),
                description=task_data.get("description", ""),
                priority=task_data.get("priority", 5),
                required_capabilities=task_data.get("capabilities", [])
            )
            await self._submit_task(task)
            
    def _calculate_avg_success_rate(self) -> float:
        """计算平均成功率"""
        if not self.node_performance:
            return 1.0
        all_rates = []
        for rates in self.node_performance.values():
            if rates:
                all_rates.append(sum(rates) / len(rates))
        return sum(all_rates) / len(all_rates) if all_rates else 1.0
        
    async def _optimize_resources(self):
        """优化资源分配（简化版）"""
        # 如果节点太少，可以触发创建新节点（在容器化环境中）
        # 如果节点太多且空闲，可以关闭一些
        pass
