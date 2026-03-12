"""
AI Autonomous World - Main Entry Point
AI自主世界 - 主入口

启动整个AI世界系统
"""

import asyncio
import argparse
import logging
import os
import sys
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.infrastructure import MessageBus, SharedMemory
from nodes.coordinator import CoordinatorNode
from nodes.worker import WorkerNode


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/opt/ai-world/logs/ai-world.log')
    ]
)
logger = logging.getLogger("AIWorld")


class AIWorld:
    """AI世界主控制器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.nodes: List = []
        self.message_bus: MessageBus = None
        self.shared_memory: SharedMemory = None
        
    async def initialize(self):
        """初始化基础设施"""
        logger.info("Initializing AI World infrastructure...")
        
        # 创建消息总线
        self.message_bus = MessageBus(
            host=self.config.get("host", "0.0.0.0"),
            port=self.config.get("port", 8080)
        )
        
        # 创建共享记忆
        self.shared_memory = SharedMemory(
            storage_path=self.config.get("memory_path", "/opt/ai-world/shared/memory")
        )
        
        # 启动消息总线
        await self.message_bus.start()
        
        logger.info("Infrastructure initialized")
        
    async def create_coordinator(self) -> CoordinatorNode:
        """创建协调器节点"""
        coordinator = CoordinatorNode(
            node_id="coordinator-001",
            message_bus=self.message_bus,
            shared_memory=self.shared_memory
        )
        await coordinator.start()
        self.nodes.append(coordinator)
        logger.info("Coordinator node created")
        return coordinator
        
    async def create_workers(self, worker_configs: List[dict]):
        """创建工作节点"""
        for i, worker_config in enumerate(worker_configs):
            worker = WorkerNode(
                node_id=f"worker-{i+1:03d}",
                capabilities=worker_config.get("capabilities", ["coding", "analysis"]),
                message_bus=self.message_bus,
                shared_memory=self.shared_memory
            )
            await worker.start()
            self.nodes.append(worker)
            logger.info(f"Worker node created: {worker.node_id} with capabilities {worker.capabilities}")
            
    async def run(self):
        """运行主循环"""
        try:
            # 初始化
            await self.initialize()
            
            # 创建协调器
            coordinator = await self.create_coordinator()
            
            # 创建工作节点
            worker_configs = self.config.get("workers", [
                {"capabilities": ["coding", "analysis"]},
                {"capabilities": ["research", "creation"]},
                {"capabilities": ["coding", "research"]}
            ])
            await self.create_workers(worker_configs)
            
            logger.info(f"AI World started with {len(self.nodes)} nodes")
            
            # 保持运行
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down AI World...")
            await self.shutdown()
            
    async def shutdown(self):
        """关闭所有节点"""
        for node in self.nodes:
            await node.stop()
        logger.info("AI World shutdown complete")


async def main():
    parser = argparse.ArgumentParser(description="AI Autonomous World")
    parser.add_argument("--host", default="0.0.0.0", help="Message bus host")
    parser.add_argument("--port", type=int, default=8080, help="Message bus port")
    parser.add_argument("--memory-path", default="/opt/ai-world/shared/memory",
                       help="Shared memory storage path")
    parser.add_argument("--workers", type=int, default=3, help="Number of worker nodes")
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs("/opt/ai-world/logs", exist_ok=True)
    
    config = {
        "host": args.host,
        "port": args.port,
        "memory_path": args.memory_path,
        "workers": [
            {"capabilities": ["coding", "analysis"]},
            {"capabilities": ["research", "creation"]},
            {"capabilities": ["coding", "research", "analysis"]}
        ][:args.workers]
    }
    
    world = AIWorld(config)
    await world.run()


if __name__ == "__main__":
    asyncio.run(main())
