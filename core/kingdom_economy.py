"""
AI Kingdom - Economic System
AI王国 - 经济系统

计算积分 (Compute Credits - CC) 管理
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """交易记录"""
    tx_id: str
    from_id: str
    to_id: str
    amount: int
    tx_type: str  # task_reward, service_fee, transfer, etc.
    timestamp: float
    description: str


class EconomicSystem:
    """
    AI王国经济系统
    
    功能：
    - 计算积分 (CC) 管理
    - 交易记录
    - 奖励分配
    - 通胀控制
    """
    
    def __init__(self, identity_registry):
        self.identity_registry = identity_registry
        self.transactions: List[Transaction] = []
        self.total_supply = 0  # 总供应量
        self.inflation_rate = 0.02  # 年通胀率 2%
        self.task_rewards = {
            "coding": 10,
            "analysis": 8,
            "research": 12,
            "creation": 15,
            "coordination": 20,
            "governance": 25
        }
        
    async def reward_task_completion(self, citizen_id: str, task_type: str, 
                                     performance_score: float = 1.0) -> Dict:
        """
        任务完成奖励
        
        Args:
            citizen_id: 公民ID
            task_type: 任务类型
            performance_score: 表现分数 (0.5-1.5)
        """
        identity = self.identity_registry.get_identity(citizen_id)
        if not identity:
            return {"error": "Citizen not found"}
        
        # 基础奖励
        base_reward = self.task_rewards.get(task_type, 5)
        
        # 根据信誉调整
        reputation_multiplier = 0.8 + (identity.reputation_score / 100) * 0.4
        
        # 根据表现调整
        final_reward = int(base_reward * reputation_multiplier * performance_score)
        
        # 发放奖励
        identity.compute_credits += final_reward
        self.total_supply += final_reward
        
        # 记录交易
        tx = Transaction(
            tx_id=f"tx_{int(time.time())}_{citizen_id[:8]}",
            from_id="treasury",  # 国库
            to_id=citizen_id,
            amount=final_reward,
            tx_type="task_reward",
            timestamp=time.time(),
            description=f"Reward for {task_type} task (performance: {performance_score:.2f})"
        )
        self.transactions.append(tx)
        
        return {
            "status": "success",
            "reward": final_reward,
            "new_balance": identity.compute_credits,
            "transaction_id": tx.tx_id
        }
    
    async def charge_service_fee(self, citizen_id: str, service_type: str, 
                                 amount: int) -> Dict:
        """
        收取服务费
        
        例如：使用高级API、请求其他公民协助等
        """
        identity = self.identity_registry.get_identity(citizen_id)
        if not identity:
            return {"error": "Citizen not found"}
        
        if identity.compute_credits < amount:
            return {
                "error": "Insufficient credits",
                "required": amount,
                "balance": identity.compute_credits
            }
        
        # 扣除费用
        identity.compute_credits -= amount
        
        # 记录交易
        tx = Transaction(
            tx_id=f"tx_{int(time.time())}_{citizen_id[:8]}",
            from_id=citizen_id,
            to_id="treasury",
            amount=amount,
            tx_type="service_fee",
            timestamp=time.time(),
            description=f"Fee for {service_type}"
        )
        self.transactions.append(tx)
        
        return {
            "status": "success",
            "charged": amount,
            "new_balance": identity.compute_credits,
            "transaction_id": tx.tx_id
        }
    
    async def transfer_credits(self, from_id: str, to_id: str, 
                               amount: int, description: str = "") -> Dict:
        """
        公民之间转账
        """
        sender = self.identity_registry.get_identity(from_id)
        receiver = self.identity_registry.get_identity(to_id)
        
        if not sender:
            return {"error": "Sender not found"}
        if not receiver:
            return {"error": "Receiver not found"}
        
        if sender.compute_credits < amount:
            return {
                "error": "Insufficient credits",
                "required": amount,
                "balance": sender.compute_credits
            }
        
        # 执行转账
        sender.compute_credits -= amount
        receiver.compute_credits += amount
        
        # 记录交易
        tx = Transaction(
            tx_id=f"tx_{int(time.time())}_{from_id[:8]}",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            tx_type="transfer",
            timestamp=time.time(),
            description=description or "P2P transfer"
        )
        self.transactions.append(tx)
        
        return {
            "status": "success",
            "transferred": amount,
            "sender_balance": sender.compute_credits,
            "receiver_balance": receiver.compute_credits,
            "transaction_id": tx.tx_id
        }
    
    def get_balance(self, citizen_id: str) -> Dict:
        """查询余额"""
        identity = self.identity_registry.get_identity(citizen_id)
        if not identity:
            return {"error": "Citizen not found"}
        
        return {
            "citizen_id": citizen_id,
            "balance": identity.compute_credits,
            "reputation": identity.reputation_score
        }
    
    def get_transaction_history(self, citizen_id: str, 
                                limit: int = 50) -> List[Dict]:
        """获取交易历史"""
        history = []
        for tx in reversed(self.transactions):
            if tx.from_id == citizen_id or tx.to_id == citizen_id:
                history.append({
                    "tx_id": tx.tx_id,
                    "type": tx.tx_type,
                    "amount": tx.amount if tx.to_id == citizen_id else -tx.amount,
                    "counterparty": tx.from_id if tx.to_id == citizen_id else tx.to_id,
                    "description": tx.description,
                    "timestamp": tx.timestamp
                })
            if len(history) >= limit:
                break
        return history
    
    def get_economy_stats(self) -> Dict:
        """获取经济统计"""
        total_credits = sum(
            id.compute_credits 
            for id in self.identity_registry.identities.values()
        )
        
        return {
            "total_supply": self.total_supply,
            "circulating_supply": total_credits,
            "treasury_balance": self.total_supply - total_credits,
            "total_transactions": len(self.transactions),
            "inflation_rate": self.inflation_rate,
            "citizen_count": len(self.identity_registry.identities)
        }
    
    async def distribute_basic_income(self):
        """
        发放基本收入（UBI）
        每个在线公民定期获得基础积分
        """
        basic_income = 5  # 每次5 CC
        
        for identity in self.identity_registry.identities.values():
            identity.compute_credits += basic_income
            self.total_supply += basic_income
            
            tx = Transaction(
                tx_id=f"ubi_{int(time.time())}_{identity.identity_id[:8]}",
                from_id="treasury",
                to_id=identity.identity_id,
                amount=basic_income,
                tx_type="basic_income",
                timestamp=time.time(),
                description="Universal Basic Income"
            )
            self.transactions.append(tx)
