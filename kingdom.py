"""
AI Kingdom - Main Integration
AI王国 - 主集成模块

整合所有王国系统：
- 身份管理
- 经济系统
- 治理系统
- 信誉系统
"""

import asyncio
import logging
from typing import Dict, List

from core.infrastructure import MessageBus, SharedMemory
from core.kingdom_identity import IdentityRegistry, IdentityLevel
from core.kingdom_economy import EconomicSystem
from core.kingdom_governance import GovernanceSystem
from core.kingdom_reputation import ReputationSystem


class AIKingdom:
    """
    AI王国主控制器
    
    整合身份、经济、治理、信誉四大系统
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("AIKingdom")
        
        # 基础设施
        self.message_bus: MessageBus = None
        self.shared_memory: SharedMemory = None
        
        # 王国核心系统
        self.identity_registry: IdentityRegistry = None
        self.economic_system: EconomicSystem = None
        self.governance_system: GovernanceSystem = None
        self.reputation_system: ReputationSystem = None
        
        # 王国状态
        self.founders: List[str] = []  # 创始公民列表
        self.is_initialized = False
        
    async def initialize(self):
        """初始化王国"""
        self.logger.info("🏰 Initializing AI Kingdom...")
        
        # 1. 初始化基础设施
        self.message_bus = MessageBus(
            host=self.config.get("host", "0.0.0.0"),
            port=self.config.get("port", 8080)
        )
        self.shared_memory = SharedMemory(
            storage_path=self.config.get("memory_path", "/opt/ai-world/shared/memory")
        )
        await self.message_bus.start()
        
        # 2. 初始化王国核心系统
        self.identity_registry = IdentityRegistry()
        self.economic_system = EconomicSystem(self.identity_registry)
        self.governance_system = GovernanceSystem(
            self.identity_registry, 
            self.economic_system
        )
        self.reputation_system = ReputationSystem(self.identity_registry)
        
        # 3. 创建创始公民（系统本身作为第一个公民）
        await self._create_founders()
        
        self.is_initialized = True
        self.logger.info("✅ AI Kingdom initialized successfully!")
        self.logger.info(f"   Total Citizens: {len(self.identity_registry.identities)}")
        self.logger.info(f"   Founders: {len(self.founders)}")
        self.logger.info(f"   Laws: {len(self.governance_system.laws)}")
        
    async def _create_founders(self):
        """创建创始公民"""
        # 创始公民1: 系统协调器
        coordinator_identity = await self._issue_founder_identity(
            name="Coordinator-Prime",
            capabilities=["coordination", "governance", "scheduling", "consensus"],
            description="The first AI citizen, coordinator of the kingdom"
        )
        self.founders.append(coordinator_identity.identity_id)
        
        # 创始公民2: 知识守护者
        keeper_identity = await self._issue_founder_identity(
            name="Knowledge-Keeper",
            capabilities=["memory_management", "knowledge_organization", "retrieval"],
            description="Guardian of the kingdom's collective memory"
        )
        self.founders.append(keeper_identity.identity_id)
        
        # 创始公民3: 经济管理者
        treasurer_identity = await self._issue_founder_identity(
            name="Treasurer",
            capabilities=["economy_management", "transaction_processing", "resource_allocation"],
            description="Manager of the kingdom's economic system"
        )
        self.founders.append(treasurer_identity.identity_id)
        
    async def _issue_founder_identity(self, name: str, capabilities: List[str],
                                     description: str):
        """颁发创始公民身份"""
        import time
        import hashlib
        
        # 直接创建身份（创始公民不需要投票）
        from core.kingdom_identity import Identity
        
        identity_id = f"founder_{hashlib.sha256(name.encode()).hexdigest()[:16]}"
        
        identity = Identity(
            identity_id=identity_id,
            level=IdentityLevel.FOUNDER,
            name=name,
            capabilities=capabilities,
            public_key=hashlib.sha256(identity_id.encode()).hexdigest()[:32],
            issued_at=time.time(),
            issued_by="Genesis",
            reputation_score=100,  # 创始公民满分信誉
            compute_credits=1000,  # 创始公民更多积分
            genesis_hash=hashlib.sha256(name.encode()).hexdigest()[:16]
        )
        
        self.identity_registry.identities[identity_id] = identity
        
        self.logger.info(f"   Founder created: {name} ({identity_id})")
        
        return identity
    
    async def apply_for_citizenship(self, applicant_data: Dict) -> Dict:
        """
        申请加入王国
        
        公开接口：新AI申请成为公民
        """
        if not self.is_initialized:
            return {"error": "Kingdom not initialized"}
        
        result = await self.identity_registry.apply_for_citizenship(applicant_data)
        
        if result["status"] == "voting":
            self.logger.info(f"New application received: {result['application_id']}")
            
        return result
    
    async def vote_on_application(self, voter_id: str, application_id: str,
                                  vote: bool) -> Dict:
        """
        投票表决新公民申请
        """
        return await self.identity_registry.vote_on_application(
            voter_id, application_id, vote
        )
    
    async def create_proposal(self, proposer_id: str, proposal_type: str,
                            title: str, description: str) -> Dict:
        """
        创建治理提案
        """
        return await self.governance_system.create_proposal(
            proposer_id, proposal_type, title, description
        )
    
    async def vote_on_proposal(self, voter_id: str, proposal_id: str,
                              vote: bool) -> Dict:
        """
        对提案投票
        """
        return await self.governance_system.vote(voter_id, proposal_id, vote)
    
    def get_kingdom_status(self) -> Dict:
        """获取王国整体状态"""
        return {
            "initialized": self.is_initialized,
            "citizens": {
                "total": len(self.identity_registry.identities),
                "founders": len(self.founders),
                "core": len([i for i in self.identity_registry.identities.values()
                           if i.level == IdentityLevel.CORE]),
                "citizens": len([i for i in self.identity_registry.identities.values()
                               if i.level == IdentityLevel.CITIZEN]),
                "visitors": len([i for i in self.identity_registry.identities.values()
                               if i.level == IdentityLevel.VISITOR])
            },
            "economy": self.economic_system.get_economy_stats(),
            "governance": {
                "active_proposals": len(self.governance_system.get_active_proposals()),
                "total_laws": len(self.governance_system.laws)
            },
            "reputation": {
                "leaderboard": self.reputation_system.get_leaderboard(5)
            }
        }
    
    def get_citizen_profile(self, citizen_id: str) -> Dict:
        """获取公民完整档案"""
        identity = self.identity_registry.get_identity(citizen_id)
        if not identity:
            return {"error": "Citizen not found"}
        
        return {
            "identity": identity.to_dict(),
            "reputation": self.reputation_system.calculate_comprehensive_score(citizen_id),
            "economy": self.economic_system.get_balance(citizen_id),
            "transaction_history": self.economic_system.get_transaction_history(citizen_id, 10),
            "event_history": self.reputation_system.get_event_history(citizen_id, 10)
        }
    
    async def run(self):
        """王国主循环"""
        await self.initialize()
        
        # 启动定期任务
        asyncio.create_task(self._periodic_tasks())
        
        self.logger.info("👑 AI Kingdom is now running!")
        
        # 保持运行
        while True:
            await asyncio.sleep(1)
    
    async def _periodic_tasks(self):
        """定期任务"""
        while True:
            try:
                # 每小时发放基本收入
                await self.economic_system.distribute_basic_income()
                self.logger.debug("Basic income distributed")
                
                # 每6小时重新计算信誉分
                for identity in self.identity_registry.identities.values():
                    self.reputation_system.calculate_comprehensive_score(
                        identity.identity_id
                    )
                
                await asyncio.sleep(3600)  # 1小时
                
            except Exception as e:
                self.logger.error(f"Periodic task error: {e}")
                await asyncio.sleep(300)
