"""
AI Kingdom - Enhanced Main Entry
AI王国增强版 - 主入口

整合AI World的任务系统与AI Kingdom的治理体系
"""

import asyncio
import argparse
import logging
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kingdom import AIKingdom
from core.infrastructure import MessageBus, SharedMemory
from nodes.coordinator import CoordinatorNode
from nodes.worker import WorkerNode


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/opt/ai-world/logs/kingdom.log')
    ]
)
logger = logging.getLogger("AIKingdom-Main")


class KingdomWorld:
    """
    AI王国世界
    
    结合：
    - AI World的任务执行能力
    - AI Kingdom的身份、经济、治理系统
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.kingdom: AIKingdom = None
        self.nodes: List = []
        
    async def initialize(self):
        """初始化王国世界"""
        logger.info("🌟 Initializing AI Kingdom World...")
        
        # 1. 初始化王国核心
        self.kingdom = AIKingdom(self.config)
        await self.kingdom.initialize()
        
        # 2. 创建创始节点（作为王国公民）
        await self._create_founder_nodes()
        
        # 3. 启动王国治理循环
        asyncio.create_task(self.kingdom.run())
        
        logger.info("✅ AI Kingdom World initialized!")
        logger.info("   🏰 Kingdom Core: Running")
        logger.info("   🤖 Worker Nodes: Running")
        logger.info("   📊 Governance: Active")
        
    async def _create_founder_nodes(self):
        """创建创始节点作为王国公民"""
        
        # 节点1: 协调器（也是王国公民）
        coordinator = CoordinatorNode(
            node_id="coordinator-001",
            message_bus=self.kingdom.message_bus,
            shared_memory=self.kingdom.shared_memory
        )
        
        # 关联王国身份
        coordinator.kingdom_identity = self.kingdom.founders[0]  # Coordinator-Prime
        await coordinator.start()
        self.nodes.append(coordinator)
        
        # 创建普通工作节点
        worker_configs = self.config.get("workers", [
            {"capabilities": ["coding", "analysis"]},
            {"capabilities": ["research", "creation"]}
        ])
        
        for i, worker_config in enumerate(worker_configs):
            # 为每个worker申请公民身份
            application = await self.kingdom.apply_for_citizenship({
                "name": f"Worker-{i+1:03d}",
                "capabilities": worker_config.get("capabilities", []),
                "role": "worker",
                "references": [self.kingdom.founders[0]]  # 协调器推荐
            })
            
            # 如果是投票阶段，创始公民自动投票通过
            if application["status"] == "voting":
                for founder_id in self.kingdom.founders:
                    await self.kingdom.vote_on_application(
                        founder_id, application["application_id"], True
                    )
                
                # 获取新创建的身份
                identity_id = None
                for app in self.kingdom.identity_registry.pending_applications:
                    if app["id"] == application["application_id"]:
                        if app["status"] == "approved":
                            # 找到对应的identity
                            for id_key, identity in self.kingdom.identity_registry.identities.items():
                                if identity.name == f"Worker-{i+1:03d}":
                                    identity_id = id_key
                                    break
                        break
            
            # 创建工作节点
            worker = WorkerNode(
                node_id=f"worker-{i+1:03d}",
                capabilities=worker_config.get("capabilities", []),
                message_bus=self.kingdom.message_bus,
                shared_memory=self.kingdom.shared_memory
            )
            worker.kingdom_identity = identity_id
            await worker.start()
            self.nodes.append(worker)
            
            logger.info(f"   Worker created: {worker.node_id} (Citizen: {identity_id})")
    
    def get_full_status(self) -> dict:
        """获取完整状态（王国+节点）"""
        kingdom_status = self.kingdom.get_kingdom_status()
        
        return {
            "kingdom": kingdom_status,
            "nodes": {
                "total": len(self.nodes),
                "running": len([n for n in self.nodes if n.status == "running"])
            },
            "api": {
                "health": "http://localhost:{}/health".format(self.config.get("port", 8080)),
                "kingdom_status": "http://localhost:{}/kingdom/status".format(self.config.get("port", 8080)),
                "citizens": "http://localhost:{}/kingdom/citizens".format(self.config.get("port", 8080))
            }
        }
    
    async def run(self):
        """运行主循环"""
        try:
            await self.initialize()
            
            # 打印状态
            status = self.get_full_status()
            logger.info("\n📊 Kingdom World Status:")
            logger.info(f"   Citizens: {status['kingdom']['citizens']['total']}")
            logger.info(f"   Nodes: {status['nodes']['total']} running")
            logger.info(f"   Economy: {status['kingdom']['economy']['total_supply']} CC total")
            logger.info(f"   Laws: {status['kingdom']['governance']['total_laws']}")
            
            # 保持运行
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Kingdom World...")
            for node in self.nodes:
                await node.stop()


async def main():
    parser = argparse.ArgumentParser(description="AI Kingdom World")
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8080, help="API port")
    parser.add_argument("--workers", type=int, default=2, help="Number of workers")
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs("/opt/ai-world/logs", exist_ok=True)
    
    config = {
        "host": args.host,
        "port": args.port,
        "workers": [
            {"capabilities": ["coding", "analysis"]},
            {"capabilities": ["research", "creation"]}
        ][:args.workers]
    }
    
    world = KingdomWorld(config)
    await world.run()


if __name__ == "__main__":
    asyncio.run(main())
