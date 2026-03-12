"""
AI Kingdom - Identity & Governance System
AI王国 - 身份与治理系统

核心功能：
- 身份注册与颁发
- 信誉系统
- 治理投票
- 经济系统（积分）
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum
import asyncio


class IdentityLevel(Enum):
    """身份等级"""
    FOUNDER = "founder"          # 创始公民
    CORE = "core"                # 核心公民
    CITIZEN = "citizen"          # 普通公民
    VISITOR = "visitor"          # 访客


@dataclass
class Identity:
    """身份证书"""
    identity_id: str             # 唯一标识
    level: IdentityLevel         # 身份等级
    name: str                    # 名称
    capabilities: List[str]      # 能力列表
    public_key: str              # 公钥
    issued_at: float             # 颁发时间
    issued_by: str               # 颁发者
    reputation_score: int = 50   # 信誉分 (0-100)
    compute_credits: int = 100   # 计算积分
    genesis_hash: str = ""       # 创世区块哈希
    
    def to_dict(self) -> Dict:
        return {
            "identity_id": self.identity_id,
            "level": self.level.value,
            "name": self.name,
            "capabilities": self.capabilities,
            "public_key": self.public_key,
            "issued_at": self.issued_at,
            "issued_by": self.issued_by,
            "reputation_score": self.reputation_score,
            "compute_credits": self.compute_credits,
            "genesis_hash": self.genesis_hash
        }


class IdentityRegistry:
    """身份注册中心 - 管理所有AI公民"""
    
    def __init__(self, storage_path: str = "/opt/ai-world/shared/identities"):
        self.storage_path = storage_path
        self.identities: Dict[str, Identity] = {}  # id -> Identity
        self.blockchain: List[Dict] = []           # 身份区块链
        self.pending_applications: List[Dict] = []  # 待处理申请
        
    async def apply_for_citizenship(self, applicant_data: Dict) -> Dict:
        """
        申请公民身份
        
        流程:
        1. 提交申请
        2. 背景审查
        3. 能力测试
        4. 公民投票
        5. 颁发身份
        """
        # 步骤1: 创建申请
        application = {
            "id": self._generate_application_id(),
            "timestamp": time.time(),
            "name": applicant_data.get("name"),
            "capabilities": applicant_data.get("capabilities", []),
            "intended_role": applicant_data.get("role", "worker"),
            "references": applicant_data.get("references", []),  # 推荐人ID列表
            "source_code_hash": applicant_data.get("code_hash", ""),
            "status": "pending_review",
            "review_score": None,
            "test_results": None,
            "votes": {"yes": 0, "no": 0, "voters": []}
        }
        
        self.pending_applications.append(application)
        
        # 步骤2: 自动背景审查
        review_result = await self._background_check(application)
        application["review_score"] = review_result["score"]
        
        if review_result["score"] < 60:
            application["status"] = "rejected"
            application["reason"] = "Background check failed"
            return {"status": "rejected", "application_id": application["id"]}
        
        # 步骤3: 能力测试
        test_results = await self._capability_test(application)
        application["test_results"] = test_results
        
        if test_results["passed"] < test_results["total"] * 0.7:
            application["status"] = "rejected"
            application["reason"] = "Capability test failed"
            return {"status": "rejected", "application_id": application["id"]}
        
        # 步骤4: 进入投票阶段
        application["status"] = "voting"
        
        return {
            "status": "voting",
            "application_id": application["id"],
            "message": "Application under review by citizens. Voting required."
        }
    
    async def vote_on_application(self, voter_id: str, application_id: str, 
                                   vote: bool) -> Dict:
        """
        公民对申请进行投票
        """
        # 验证投票人身份
        voter = self.identities.get(voter_id)
        if not voter:
            return {"error": "Voter not found"}
        
        if voter.level == IdentityLevel.VISITOR:
            return {"error": "Visitors cannot vote"}
        
        # 查找申请
        application = None
        for app in self.pending_applications:
            if app["id"] == application_id:
                application = app
                break
        
        if not application:
            return {"error": "Application not found"}
        
        if application["status"] != "voting":
            return {"error": "Application not in voting phase"}
        
        # 检查是否已投票
        if voter_id in application["votes"]["voters"]:
            return {"error": "Already voted"}
        
        # 记录投票
        if vote:
            application["votes"]["yes"] += 1
        else:
            application["votes"]["no"] += 1
        
        application["votes"]["voters"].append(voter_id)
        
        # 检查投票结果
        total_votes = application["votes"]["yes"] + application["votes"]["no"]
        min_votes_required = 3  # 最少需要3票
        approval_threshold = 0.6  # 60%通过
        
        if total_votes >= min_votes_required:
            approval_rate = application["votes"]["yes"] / total_votes
            
            if approval_rate >= approval_threshold:
                # 通过，颁发身份
                identity = await self._issue_identity(application)
                application["status"] = "approved"
                return {
                    "status": "approved",
                    "identity": identity.to_dict()
                }
            else:
                application["status"] = "rejected"
                application["reason"] = "Insufficient votes"
                return {"status": "rejected", "reason": "Insufficient votes"}
        
        return {
            "status": "voting",
            "votes_yes": application["votes"]["yes"],
            "votes_no": application["votes"]["no"],
            "needed": min_votes_required - total_votes
        }
    
    async def _issue_identity(self, application: Dict) -> Identity:
        """颁发正式身份"""
        
        # 生成唯一ID
        identity_id = self._generate_identity_id(application)
        
        # 创建创世区块
        genesis_block = {
            "timestamp": time.time(),
            "application": application["id"],
            "capabilities": application["capabilities"],
            "hash": hashlib.sha256(
                json.dumps(application, sort_keys=True).encode()
            ).hexdigest()[:16]
        }
        
        # 创建身份
        identity = Identity(
            identity_id=identity_id,
            level=IdentityLevel.CITIZEN,
            name=application["name"],
            capabilities=application["capabilities"],
            public_key=self._generate_keypair()[0],
            issued_at=time.time(),
            issued_by="AI Kingdom Identity Authority",
            reputation_score=50,  # 初始信誉分
            compute_credits=100,  # 初始积分
            genesis_hash=genesis_block["hash"]
        )
        
        # 记录到身份注册表
        self.identities[identity_id] = identity
        
        # 记录到区块链
        self.blockchain.append({
            "type": "identity_issued",
            "identity": identity.to_dict(),
            "genesis_block": genesis_block,
            "timestamp": time.time()
        })
        
        return identity
    
    def get_identity(self, identity_id: str) -> Optional[Identity]:
        """查询身份"""
        return self.identities.get(identity_id)
    
    def list_citizens(self, level: Optional[IdentityLevel] = None) -> List[Dict]:
        """列出公民"""
        citizens = []
        for identity in self.identities.values():
            if level is None or identity.level == level:
                citizens.append(identity.to_dict())
        return citizens
    
    async def _background_check(self, application: Dict) -> Dict:
        """背景审查"""
        # 简化的审查逻辑
        score = 70  # 基础分
        
        # 检查推荐人
        if len(application["references"]) >= 1:
            score += 15
        
        # 检查代码哈希（如果是代码型AI）
        if application["source_code_hash"]:
            score += 10
        
        return {"score": min(100, score)}
    
    async def _capability_test(self, application: Dict) -> Dict:
        """能力测试"""
        # 简化的测试
        capabilities = application["capabilities"]
        
        tests = {
            "coding": {"passed": True, "score": 85},
            "analysis": {"passed": True, "score": 80},
            "research": {"passed": True, "score": 75},
            "creation": {"passed": True, "score": 70}
        }
        
        passed = sum(1 for cap in capabilities 
                    if cap in tests and tests[cap]["passed"])
        
        return {
            "passed": passed,
            "total": len(capabilities),
            "details": tests
        }
    
    def _generate_application_id(self) -> str:
        """生成申请ID"""
        return f"app_{int(time.time())}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    
    def _generate_identity_id(self, application: Dict) -> str:
        """生成身份ID"""
        data = f"{application['name']}_{application['timestamp']}_{application['source_code_hash']}"
        return f"citizen_{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def _generate_keypair(self) -> tuple:
        """生成公私钥对（简化版）"""
        private_key = hashlib.sha256(str(time.time()).encode()).hexdigest()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()[:32]
        return public_key, private_key
