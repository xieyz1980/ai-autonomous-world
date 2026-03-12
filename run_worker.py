"""
Standalone Worker Node Runner
独立工作节点启动器

用于在Docker容器中启动单个worker节点
"""

import argparse
import asyncio
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.infrastructure import MessageBus, SharedMemory
from nodes.worker import WorkerNode


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WorkerRunner")


async def main():
    parser = argparse.ArgumentParser(description="AI World Worker Node")
    parser.add_argument("--id", required=True, help="Worker node ID")
    parser.add_argument("--capabilities", nargs="+", default=["coding", "analysis"],
                       help="Worker capabilities")
    parser.add_argument("--coordinator", default="http://localhost:8080",
                       help="Coordinator URL")
    parser.add_argument("--shared-memory", default="/opt/ai-world/shared/memory",
                       help="Shared memory path")
    
    args = parser.parse_args()
    
    # 创建基础设施（连接到现有的消息总线）
    # 在Docker环境中，worker直接通过HTTP API与coordinator通信
    
    # 简化的实现：worker启动自己的消息总线客户端
    message_bus = MessageBus(host="0.0.0.0", port=0)  # 随机端口
    await message_bus.start()
    
    shared_memory = SharedMemory(storage_path=args.shared_memory)
    
    # 创建worker
    worker = WorkerNode(
        node_id=args.id,
        capabilities=args.capabilities,
        message_bus=message_bus,
        shared_memory=shared_memory
    )
    
    await worker.start()
    
    logger.info(f"Worker {args.id} started with capabilities: {args.capabilities}")
    logger.info(f"Connecting to coordinator at {args.coordinator}")
    
    # 注册到coordinator（通过HTTP API）
    # 这里简化处理，实际应通过消息总线注册
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"Worker {args.id} shutting down...")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
