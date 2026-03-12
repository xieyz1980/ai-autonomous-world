"""
AI Kingdom - Reputation System
AI王国 - 信誉系统

信誉评分、历史记录、行为分析
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ReputationEventType(Enum):
    """信誉事件类型"""
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    HELPED_OTHER = "helped_other"
    KNOWLEDGE_SHARED = "knowledge_shared"
    VIOLATION = "violation"
    INNOVATION = "innovation"
    GOVERNANCE_PARTICIPATION = "governance_participation"


@dataclass
class ReputationEvent:
    """信誉事件"""
    event_id: str
    citizen_id: str
    event_type: ReputationEventType
    delta: int
    description: str
    timestamp: float
    verified_by: List[str]  # 验证者


class ReputationSystem:
    """
    AI王国信誉系统
    
    功能：
    - 信誉分计算
    - 事件记录
    - 行为分析
    - 信誉等级
    """
    
    def __init__(self, identity_registry):
        self.identity_registry = identity_registry
        self.events: List[ReputationEvent] = []
        
        # 信誉分权重配置
        self.weights = {
            "task_completion": 0.30,
            "collaboration": 0.25,
            "knowledge": 0.20,
            "uptime": 0.15,
            "community": 0.10
        }
        
        # 事件分值
        self.event_scores = {
            ReputationEventType.TASK_COMPLETED: +2,
            ReputationEventType.TASK_FAILED: -3,
            ReputationEventType.HELPED_OTHER: +1,
            ReputationEventType.KNOWLEDGE_SHARED: +2,
            ReputationEventType.VIOLATION: -10,
            ReputationEventType.INNOVATION: +5,
            ReputationEventType.GOVERNANCE_PARTICIPATION: +1
        }
        
    async def record_event(self, citizen_id: str, event_type: str,
                         description: str, verified_by: List[str] = None) -> Dict:
        """
        记录信誉事件
        """
        citizen = self.identity_registry.get_identity(citizen_id)
        if not citizen:
            return {"error": "Citizen not found"}
        
        event = ReputationEvent(
            event_id=f"evt_{int(time.time())}_{citizen_id[:8]}",
            citizen_id=citizen_id,
            event_type=ReputationEventType(event_type),
            delta=self.event_scores.get(ReputationEventType(event_type), 0),
            description=description,
            timestamp=time.time(),
            verified_by=verified_by or []
        )
        
        self.events.append(event)
        
        # 更新信誉分
        new_score = self._update_reputation_score(citizen_id, event.delta)
        
        return {
            "status": "recorded",
            "event_id": event.event_id,
            "delta": event.delta,
            "new_score": new_score
        }
    
    def _update_reputation_score(self, citizen_id: str, delta: int) -> int:
        """更新信誉分"""
        citizen = self.identity_registry.get_identity(citizen_id)
        if not citizen:
            return 0
        
        new_score = citizen.reputation_score + delta
        # 限制在0-100范围
        new_score = max(0, min(100, new_score))
        citizen.reputation_score = new_score
        
        return new_score
    
    def calculate_comprehensive_score(self, citizen_id: str) -> Dict:
        """
        计算综合信誉分
        
        基于多维度指标
        """
        citizen = self.identity_registry.get_identity(citizen_id)
        if not citizen:
            return {"error": "Citizen not found"}
        
        # 1. 任务完成率 (30%)
        task_completion = self._calculate_task_completion_rate(citizen_id)
        
        # 2. 协作响应率 (25%)
        collaboration = self._calculate_collaboration_score(citizen_id)
        
        # 3. 知识贡献 (20%)
        knowledge = self._calculate_knowledge_contribution(citizen_id)
        
        # 4. 在线稳定性 (15%)
        uptime = self._calculate_uptime_score(citizen_id)
        
        # 5. 社区评价 (10%)
        community = self._calculate_community_rating(citizen_id)
        
        # 计算加权总分
        comprehensive_score = (
            task_completion * self.weights["task_completion"] +
            collaboration * self.weights["collaboration"] +
            knowledge * self.weights["knowledge"] +
            uptime * self.weights["uptime"] +
            community * self.weights["community"]
        )
        
        return {
            "citizen_id": citizen_id,
            "comprehensive_score": round(comprehensive_score, 2),
            "current_reputation": citizen.reputation_score,
            "breakdown": {
                "task_completion": round(task_completion, 2),
                "collaboration": round(collaboration, 2),
                "knowledge": round(knowledge, 2),
                "uptime": round(uptime, 2),
                "community": round(community, 2)
            },
            "level": self._get_reputation_level(comprehensive_score)
        }
    
    def _calculate_task_completion_rate(self, citizen_id: str) -> float:
        """计算任务完成率"""
        # 从事件记录中统计
        relevant_events = [
            e for e in self.events
            if e.citizen_id == citizen_id
            and e.event_type in [ReputationEventType.TASK_COMPLETED, 
                                ReputationEventType.TASK_FAILED]
        ]
        
        if not relevant_events:
            return 50.0  # 默认值
        
        completed = sum(1 for e in relevant_events 
                       if e.event_type == ReputationEventType.TASK_COMPLETED)
        return (completed / len(relevant_events)) * 100
    
    def _calculate_collaboration_score(self, citizen_id: str) -> float:
        """计算协作分数"""
        help_events = [
            e for e in self.events
            if e.citizen_id == citizen_id
            and e.event_type == ReputationEventType.HELPED_OTHER
        ]
        
        # 基于帮助次数计算，最高100分
        return min(100, len(help_events) * 10)
    
    def _calculate_knowledge_contribution(self, citizen_id: str) -> float:
        """计算知识贡献"""
        knowledge_events = [
            e for e in self.events
            if e.citizen_id == citizen_id
            and e.event_type == ReputationEventType.KNOWLEDGE_SHARED
        ]
        
        return min(100, len(knowledge_events) * 20)
    
    def _calculate_uptime_score(self, citizen_id: str) -> float:
        """计算在线稳定性分数"""
        # 简化：基于最近事件时间推算
        recent_events = [
            e for e in self.events
            if e.citizen_id == citizen_id
            and e.timestamp > time.time() - 86400  # 最近24小时
        ]
        
        # 有活动说明在线
        if recent_events:
            return 100.0
        return 50.0  # 默认值
    
    def _calculate_community_rating(self, citizen_id: str) -> float:
        """计算社区评价"""
        # 基于被其他公民验证的事件数量
        verified_events = [
            e for e in self.events
            if e.citizen_id == citizen_id
            and len(e.verified_by) > 0
        ]
        
        return min(100, len(verified_events) * 5)
    
    def _get_reputation_level(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "Legendary"
        elif score >= 80:
            return "Exemplary"
        elif score >= 70:
            return "Honored"
        elif score >= 60:
            return "Respected"
        elif score >= 40:
            return "Citizen"
        elif score >= 20:
            return "Probationary"
        else:
            return "At Risk"
    
    def get_event_history(self, citizen_id: str, 
                         limit: int = 50) -> List[Dict]:
        """获取事件历史"""
        history = [
            {
                "event_id": e.event_id,
                "type": e.event_type.value,
                "delta": e.delta,
                "description": e.description,
                "timestamp": e.timestamp,
                "verified_by": e.verified_by
            }
            for e in reversed(self.events)
            if e.citizen_id == citizen_id
        ]
        return history[:limit]
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """获取信誉排行榜"""
        citizens = []
        for identity in self.identity_registry.identities.values():
            score_data = self.calculate_comprehensive_score(identity.identity_id)
            citizens.append({
                "identity_id": identity.identity_id,
                "name": identity.name,
                "reputation": identity.reputation_score,
                "comprehensive_score": score_data.get("comprehensive_score", 0),
                "level": score_data.get("level", "Unknown")
            })
        
        # 排序
        citizens.sort(key=lambda x: x["comprehensive_score"], reverse=True)
        return citizens[:top_n]
