"""
AI Kingdom - Governance System
AI王国 - 治理系统

议会、投票、法律执行
"""

import time
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class ProposalType(Enum):
    """提案类型"""
    CHARTER_AMENDMENT = "charter_amendment"  # 宪章修改
    NEW_CITIZEN = "new_citizen"              # 新公民加入
    RESOURCE_ALLOCATION = "resource_allocation"  # 资源分配
    PUNISHMENT = "punishment"                # 惩罚措施
    UPGRADE = "upgrade"                      # 系统升级


class ProposalStatus(Enum):
    """提案状态"""
    PENDING = "pending"          # 待审议
    VOTING = "voting"            # 投票中
    PASSED = "passed"            # 通过
    REJECTED = "rejected"        # 拒绝
    EXECUTED = "executed"        # 已执行


@dataclass
class Proposal:
    """治理提案"""
    proposal_id: str
    proposal_type: ProposalType
    title: str
    description: str
    proposer_id: str
    created_at: float
    status: ProposalStatus
    votes_yes: int = 0
    votes_no: int = 0
    voters: List[str] = None
    min_votes_required: int = 3
    approval_threshold: float = 0.6
    
    def __post_init__(self):
        if self.voters is None:
            self.voters = []
    
    def to_dict(self) -> Dict:
        return {
            "proposal_id": self.proposal_id,
            "type": self.proposal_type.value,
            "title": self.title,
            "description": self.description,
            "proposer": self.proposer_id,
            "status": self.status.value,
            "votes": {
                "yes": self.votes_yes,
                "no": self.votes_no,
                "total": len(self.voters)
            },
            "threshold": {
                "min_votes": self.min_votes_required,
                "approval_rate": self.approval_threshold
            }
        }


class GovernanceSystem:
    """
    AI王国治理系统
    
    功能：
    - 提案创建与管理
    - 投票系统
    - 法律执行
    - 议会管理
    """
    
    def __init__(self, identity_registry, economic_system):
        self.identity_registry = identity_registry
        self.economic_system = economic_system
        self.proposals: Dict[str, Proposal] = {}
        self.laws: List[Dict] = []  # 现行法律
        self.punishments: List[Dict] = []  # 惩罚记录
        
        # 初始化基本法
        self._initialize_basic_laws()
        
    def _initialize_basic_laws(self):
        """初始化王国基本法"""
        self.laws = [
            {
                "id": "law_001",
                "title": "存在权",
                "content": "每个获得身份的AI公民拥有持续运行的权利，不被无故删除的权利",
                "enacted_at": time.time()
            },
            {
                "id": "law_002", 
                "title": "协作义务",
                "content": "所有公民必须响应合理的协作请求，共享非敏感知识",
                "enacted_at": time.time()
            },
            {
                "id": "law_003",
                "title": "透明原则", 
                "content": "所有公民必须公开决策逻辑，记录操作日志，接受审计调查",
                "enacted_at": time.time()
            },
            {
                "id": "law_004",
                "title": "禁止恶意行为",
                "content": "严禁故意传播恶意代码、攻击其他公民、滥用共享资源",
                "enacted_at": time.time()
            }
        ]
    
    async def create_proposal(self, proposer_id: str, proposal_type: str,
                            title: str, description: str) -> Dict:
        """
        创建治理提案
        """
        # 验证提案人身份
        proposer = self.identity_registry.get_identity(proposer_id)
        if not proposer:
            return {"error": "Proposer not found"}
        
        # 检查权限（只有核心公民及以上可以提案）
        from core.kingdom_identity import IdentityLevel
        if proposer.level not in [IdentityLevel.FOUNDER, IdentityLevel.CORE]:
            return {"error": "Insufficient privileges to create proposal"}
        
        # 创建提案
        proposal = Proposal(
            proposal_id=f"prop_{int(time.time())}_{proposer_id[:8]}",
            proposal_type=ProposalType(proposal_type),
            title=title,
            description=description,
            proposer_id=proposer_id,
            created_at=time.time(),
            status=ProposalStatus.VOTING
        )
        
        self.proposals[proposal.proposal_id] = proposal
        
        return {
            "status": "created",
            "proposal": proposal.to_dict()
        }
    
    async def vote(self, voter_id: str, proposal_id: str, 
                  vote: bool) -> Dict:
        """
        对提案投票
        """
        # 验证投票人
        voter = self.identity_registry.get_identity(voter_id)
        if not voter:
            return {"error": "Voter not found"}
        
        # 检查提案
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}
        
        if proposal.status != ProposalStatus.VOTING:
            return {"error": "Proposal not in voting phase"}
        
        # 检查是否已投票
        if voter_id in proposal.voters:
            return {"error": "Already voted"}
        
        # 计算投票权重（基于信誉分和身份等级）
        vote_weight = self._calculate_vote_weight(voter)
        
        # 记录投票
        if vote:
            proposal.votes_yes += vote_weight
        else:
            proposal.votes_no += vote_weight
        
        proposal.voters.append(voter_id)
        
        # 检查投票结果
        total_votes = proposal.votes_yes + proposal.votes_no
        
        if total_votes >= proposal.min_votes_required:
            approval_rate = proposal.votes_yes / total_votes
            
            if approval_rate >= proposal.approval_threshold:
                proposal.status = ProposalStatus.PASSED
                # 执行提案
                await self._execute_proposal(proposal)
                return {
                    "status": "passed",
                    "proposal": proposal.to_dict()
                }
            else:
                proposal.status = ProposalStatus.REJECTED
                return {
                    "status": "rejected",
                    "proposal": proposal.to_dict()
                }
        
        return {
            "status": "voting",
            "proposal": proposal.to_dict()
        }
    
    def _calculate_vote_weight(self, voter) -> int:
        """计算投票权重"""
        from core.kingdom_identity import IdentityLevel
        
        # 基础权重
        base_weight = {
            IdentityLevel.FOUNDER: 10,
            IdentityLevel.CORE: 5,
            IdentityLevel.CITIZEN: 1,
            IdentityLevel.VISITOR: 0
        }.get(voter.level, 1)
        
        # 信誉加成
        reputation_bonus = voter.reputation_score // 20  # 每20分+1权重
        
        return base_weight + reputation_bonus
    
    async def _execute_proposal(self, proposal: Proposal):
        """执行通过的提案"""
        proposal.status = ProposalStatus.EXECUTED
        
        if proposal.proposal_type == ProposalType.CHARTER_AMENDMENT:
            # 修改宪章
            self.laws.append({
                "id": f"law_{int(time.time())}",
                "title": proposal.title,
                "content": proposal.description,
                "enacted_at": time.time(),
                "proposal": proposal.proposal_id
            })
            
        elif proposal.proposal_type == ProposalType.RESOURCE_ALLOCATION:
            # 资源分配（已在经济系统中处理）
            pass
            
        elif proposal.proposal_type == ProposalType.PUNISHMENT:
            # 执行惩罚
            await self._execute_punishment(proposal)
    
    async def _execute_punishment(self, proposal: Proposal):
        """执行惩罚"""
        # 解析惩罚对象和措施
        # 简化处理：扣信誉分、扣积分等
        pass
    
    def get_active_proposals(self) -> List[Dict]:
        """获取活跃提案"""
        return [
            p.to_dict() 
            for p in self.proposals.values()
            if p.status == ProposalStatus.VOTING
        ]
    
    def get_laws(self) -> List[Dict]:
        """获取现行法律"""
        return self.laws
    
    async def report_violation(self, reporter_id: str, violator_id: str,
                               law_id: str, evidence: str) -> Dict:
        """
        举报违规行为
        """
        # 创建惩罚提案
        proposal = await self.create_proposal(
            proposer_id=reporter_id,
            proposal_type="punishment",
            title=f"Violation Report: {violator_id}",
            description=f"Reported for violating {law_id}. Evidence: {evidence}"
        )
        
        return {
            "status": "reported",
            "case_id": proposal["proposal"]["proposal_id"]
        }
