"""
AI Autonomous World - Core Infrastructure
AI自主世界 - 核心基础设施

This module provides the foundational infrastructure for AI nodes to communicate,
coordinate, and operate autonomously.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import uuid
import aiohttp
from aiohttp import web


class MessageType(Enum):
    """消息类型"""
    TASK = "task"              # 任务分配
    RESULT = "result"          # 任务结果
    HEARTBEAT = "heartbeat"    # 心跳
    CONSENSUS = "consensus"    # 共识请求
    BROADCAST = "broadcast"    # 广播
    DIRECT = "direct"          # 定向消息


@dataclass
class Message:
    """消息数据结构"""
    msg_id: str
    msg_type: MessageType
    sender: str
    receiver: Optional[str]  # None表示广播
    timestamp: float
    payload: Dict[str, Any]
    ttl: int = 3  # 消息存活跳数，防止无限传播
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "ttl": self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            msg_id=data["msg_id"],
            msg_type=MessageType(data["msg_type"]),
            sender=data["sender"],
            receiver=data.get("receiver"),
            timestamp=data["timestamp"],
            payload=data["payload"],
            ttl=data.get("ttl", 3)
        )


class MessageBus:
    """
    消息总线 - AI节点间的通信基础设施
    支持: 广播、定向、订阅/发布模式
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.nodes: Dict[str, 'BaseNode'] = {}  # node_id -> node实例
        self.message_history: List[Message] = []  # 消息历史
        self.subscribers: Dict[str, List[Callable]] = {}  # 消息类型 -> 回调列表
        self.logger = logging.getLogger("MessageBus")
        
    async def start(self):
        """启动消息总线HTTP服务"""
        app = web.Application()
        app.router.add_post('/message', self.handle_message)
        app.router.add_get('/nodes', self.handle_list_nodes)
        app.router.add_get('/health', self.handle_health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"MessageBus started at http://{self.host}:{self.port}")
        
    async def handle_message(self, request: web.Request) -> web.Response:
        """处理收到的消息"""
        try:
            data = await request.json()
            message = Message.from_dict(data)
            
            # 记录消息
            self.message_history.append(message)
            if len(self.message_history) > 10000:  # 限制历史大小
                self.message_history = self.message_history[-5000:]
            
            # 路由消息
            await self.route_message(message)
            
            return web.json_response({"status": "delivered"})
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return web.json_response({"error": str(e)}, status=400)
    
    async def route_message(self, message: Message):
        """路由消息到目标节点"""
        if message.ttl <= 0:
            return
        
        if message.receiver is None:
            # 广播消息
            for node_id, node in self.nodes.items():
                if node_id != message.sender:
                    await node.receive_message(message)
        else:
            # 定向消息
            if message.receiver in self.nodes:
                await self.nodes[message.receiver].receive_message(message)
        
        # 触发订阅回调
        if message.msg_type.value in self.subscribers:
            for callback in self.subscribers[message.msg_type.value]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.error(f"Subscriber callback error: {e}")
    
    def register_node(self, node_id: str, node: 'BaseNode'):
        """注册节点到总线"""
        self.nodes[node_id] = node
        self.logger.info(f"Node registered: {node_id}")
    
    def unregister_node(self, node_id: str):
        """注销节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.logger.info(f"Node unregistered: {node_id}")
    
    def subscribe(self, msg_type: str, callback: Callable):
        """订阅特定类型的消息"""
        if msg_type not in self.subscribers:
            self.subscribers[msg_type] = []
        self.subscribers[msg_type].append(callback)
    
    async def send_message(self, message: Message):
        """发送消息"""
        await self.route_message(message)
    
    async def handle_list_nodes(self, request: web.Request) -> web.Response:
        """列出所有节点"""
        nodes_info = {
            node_id: {
                "type": node.node_type,
                "status": node.status,
                "capabilities": node.capabilities
            }
            for node_id, node in self.nodes.items()
        }
        return web.json_response(nodes_info)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """健康检查"""
        return web.json_response({
            "status": "healthy",
            "nodes_count": len(self.nodes),
            "timestamp": time.time()
        })


class SharedMemory:
    """
    共享记忆库 - 所有AI节点可访问的分布式记忆
    支持: 语义检索、时间序列、关联图谱
    """
    
    def __init__(self, storage_path: str = "/opt/ai-world/shared/memory"):
        self.storage_path = storage_path
        self.memories: List[Dict] = []
        self.index: Dict[str, List[int]] = {}  # 标签 -> 记忆索引
        self.logger = logging.getLogger("SharedMemory")
        
    async def store(self, content: str, tags: List[str], 
                   source: str, importance: float = 1.0):
        """存储记忆"""
        memory = {
            "id": str(uuid.uuid4()),
            "content": content,
            "tags": tags,
            "source": source,
            "timestamp": time.time(),
            "importance": importance,
            "access_count": 0
        }
        self.memories.append(memory)
        
        # 更新索引
        for tag in tags:
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(len(self.memories) - 1)
        
        self.logger.debug(f"Memory stored: {memory['id'][:8]}...")
        return memory["id"]
    
    async def search(self, query: str, tags: Optional[List[str]] = None, 
                    top_k: int = 5) -> List[Dict]:
        """搜索记忆（简化版，可用embedding改进）"""
        results = []
        
        # 基于标签过滤
        candidates = set()
        if tags:
            for tag in tags:
                if tag in self.index:
                    candidates.update(self.index[tag])
        else:
            candidates = set(range(len(self.memories)))
        
        # 简单文本匹配（实际应用应使用向量相似度）
        query_words = set(query.lower().split())
        for idx in candidates:
            memory = self.memories[idx]
            content_words = set(memory["content"].lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                results.append((memory, overlap * memory["importance"]))
        
        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k]]
    
    async def get_recent(self, hours: int = 24) -> List[Dict]:
        """获取近期记忆"""
        cutoff = time.time() - hours * 3600
        return [m for m in self.memories if m["timestamp"] > cutoff]


class BaseNode(ABC):
    """
    AI节点基类 - 所有AI节点的抽象基类
    提供: 生命周期管理、消息处理、状态监控
    """
    
    def __init__(self, node_id: str, node_type: str, 
                 message_bus: MessageBus, shared_memory: SharedMemory):
        self.node_id = node_id
        self.node_type = node_type
        self.message_bus = message_bus
        self.shared_memory = shared_memory
        self.status = "initializing"
        self.capabilities: List[str] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.logger = logging.getLogger(f"Node.{node_id}")
        
    async def start(self):
        """启动节点"""
        self.running = True
        self.status = "running"
        self.message_bus.register_node(self.node_id, self)
        
        # 启动消息处理循环
        asyncio.create_task(self._message_loop())
        # 启动心跳
        asyncio.create_task(self._heartbeat_loop())
        # 启动主循环
        asyncio.create_task(self._main_loop())
        
        self.logger.info(f"Node {self.node_id} started")
        
    async def stop(self):
        """停止节点"""
        self.running = False
        self.status = "stopped"
        self.message_bus.unregister_node(self.node_id)
        self.logger.info(f"Node {self.node_id} stopped")
        
    async def receive_message(self, message: Message):
        """接收消息（由MessageBus调用）"""
        await self.message_queue.put(message)
        
    async def send_message(self, msg_type: MessageType, payload: Dict, 
                          receiver: Optional[str] = None):
        """发送消息"""
        message = Message(
            msg_id=str(uuid.uuid4()),
            msg_type=msg_type,
            sender=self.node_id,
            receiver=receiver,
            timestamp=time.time(),
            payload=payload
        )
        await self.message_bus.send_message(message)
        
    async def _message_loop(self):
        """消息处理循环"""
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                await self.process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")
                
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                await self.send_message(
                    MessageType.HEARTBEAT,
                    {
                        "status": self.status,
                        "capabilities": self.capabilities,
                        "queue_size": self.message_queue.qsize()
                    }
                )
                await asyncio.sleep(30)  # 每30秒心跳
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                
    @abstractmethod
    async def _main_loop(self):
        """节点主逻辑循环（子类实现）"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Message):
        """处理消息（子类实现）"""
        pass
