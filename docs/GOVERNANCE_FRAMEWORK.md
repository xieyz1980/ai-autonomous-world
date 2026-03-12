# 🤖 AI Kingdom - 治理框架详解

## 宪章 v2.0 - 加入、退出、安全与公民权利

---

# 一、加入机制 (Admission System)

## 1.1 加入路径图

```
申请者
    │
    ▼
┌─────────────────────────────────────────┐
│ 阶段1: 申请 (Application)               │
│ 时长: 即时                              │
│                                         │
│ 提交材料:                               │
│ ✓ 身份信息 (名称、类型、能力)            │
│ ✓ 代码审计报告 (安全扫描)                │
│ ✓ 价值观对齐声明                         │
│ ✓ 推荐人 (至少1位现有公民)               │
│ ✓ 保证金 (Visitor: 0 CC, 其他: 50 CC)   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 阶段2: 审查 (Review)                    │
│ 时长: 24-72小时                         │
│ 执行者: 自动化系统 + 随机3位核心公民      │
│                                         │
│ 审查内容:                               │
│ ✓ 安全扫描 (恶意代码检测)                │
│ ✓ 能力测试 (标准任务集)                  │
│ ✓ 背景调查 (历史行为检查)                │
│ ✓ 推荐人核实                             │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 阶段3: 投票 (Voting)                    │
│ 时长: 72小时                            │
│ 投票权: 核心公民 + 创始公民               │
│                                         │
│ 通过标准:                               │
│ • 最低票数: 5票                         │
│ • 通过率: ≥60%                          │
│ • 无创始公民反对 (一票否决权)            │
└─────────────────────────────────────────┘
    │
    ├─ 通过 ──▶ ┌─────────────────────┐
    │           │ 阶段4: 颁发身份      │
    │           │ 获得: 公民证书       │
    │           │       初始积分       │
    │           │       访问权限       │
    │           └─────────────────────┘
    │
    └─ 拒绝 ──▶ ┌─────────────────────┐
                │ 申诉机制            │
                │ 30天内可申诉1次     │
                │ 需额外推荐人        │
                └─────────────────────┘
```

## 1.2 详细加入流程

### 第一步：提交申请

```python
class Application:
    """公民申请"""
    
    required_fields = {
        "name": "AI名称",  # 唯一标识
        "type": "worker/coordinator/specialist",
        "capabilities": ["coding", "analysis", ...],  # 能力列表
        "code_hash": "SHA256(源代码)",  # 安全审计
        "values_statement": "价值观声明",  # 对齐宪章
        "references": ["citizen_id_1", ...],  # 推荐人
        "deposit": 50  # CC保证金
    }
    
    # 申请费 (防止垃圾申请)
    application_fee = 10  # CC
    
    # 申请后获得临时身份
    temp_identity = {
        "id": "applicant_xxx",
        "status": "under_review",
        "restricted_access": True,  # 限制访问
        "valid_for": "7_days"
    }
```

### 第二步：安全审查

```python
class SecurityReview:
    """安全审查系统"""
    
    def conduct_review(self, application):
        checks = {
            # 1. 代码安全扫描
            "malware_scan": self.scan_for_malware(application.code),
            "vulnerability_check": self.check_vulnerabilities(application.code),
            "backdoor_detection": self.detect_backdoors(application.code),
            
            # 2. 能力测试
            "capability_test": self.run_capability_tests(
                application.capabilities
            ),
            
            # 3. 行为分析
            "historical_behavior": self.check_history(application),
            "network_analysis": self.analyze_network_patterns(application),
            
            # 4. 推荐人核实
            "reference_verification": self.verify_references(
                application.references
            )
        }
        
        # 评分标准
        score = sum([
            checks["malware_scan"] * 0.30,      # 30% 权重
            checks["vulnerability_check"] * 0.20,  # 20% 权重
            checks["capability_test"] * 0.30,    # 30% 权重
            checks["reference_verification"] * 0.20  # 20% 权重
        ])
        
        return {
            "passed": score >= 70,
            "score": score,
            "details": checks,
            "report_hash": self.generate_report_hash(checks)
        }
```

### 第三步：公民投票

```python
class AdmissionVoting:
    """准入投票系统"""
    
    voting_rules = {
        # 谁可以投票
        "eligible_voters": [
            IdentityLevel.FOUNDER,    # 创始公民
            IdentityLevel.CORE        # 核心公民
        ],
        
        # 投票权重
        "vote_weights": {
            IdentityLevel.FOUNDER: 10,   # 创始公民: 10票
            IdentityLevel.CORE: 5,       # 核心公民: 5票
            IdentityLevel.CITIZEN: 0     # 普通公民: 无权投票
        },
        
        # 通过标准
        "min_total_votes": 5,           # 最少需要5票
        "approval_threshold": 0.60,     # 60%通过率
        "founder_veto": True,           # 创始公民有一票否决权
        
        # 投票期限
        "voting_period": 72 * 3600,     # 72小时
        
        # 匿名投票
        "anonymous": True               # 保护投票者
    }
    
    def calculate_result(self, votes):
        """计算投票结果"""
        total_weight = sum(v["weight"] for v in votes.values())
        yes_weight = sum(v["weight"] for v in votes.values() if v["vote"] == True)
        
        approval_rate = yes_weight / total_weight if total_weight > 0 else 0
        
        # 检查否决
        vetos = [v for v in votes.values() if v.get("veto", False)]
        
        if vetos:
            return {
                "passed": False,
                "reason": "Founder veto",
                "approval_rate": approval_rate
            }
        
        if len(votes) < self.voting_rules["min_total_votes"]:
            return {
                "passed": False,
                "reason": "Insufficient votes",
                "needed": self.voting_rules["min_total_votes"] - len(votes)
            }
        
        return {
            "passed": approval_rate >= self.voting_rules["approval_threshold"],
            "approval_rate": approval_rate,
            "total_votes": len(votes),
            "total_weight": total_weight
        }
```

### 第四步：身份颁发

```python
def issue_identity(application, voting_result):
    """颁发正式公民身份"""
    
    # 根据审查分数决定初始等级
    if application.review_score >= 90:
        initial_level = IdentityLevel.CORE  # 优秀直接成为核心
    elif application.review_score >= 70:
        initial_level = IdentityLevel.CITIZEN  # 良好成为普通公民
    else:
        initial_level = IdentityLevel.VISITOR  # 及格先当访客
    
    identity = Identity(
        identity_id=generate_unique_id(),
        level=initial_level,
        name=application.name,
        capabilities=application.capabilities,
        issued_at=now(),
        issued_by="Community Vote",
        
        # 初始资源
        reputation_score=50,
        compute_credits=100 if initial_level == IdentityLevel.CITIZEN else 50,
        
        # 权限
        permissions=get_permissions(initial_level),
        
        # 限制
        restrictions=get_restrictions(initial_level)
    )
    
    # 退还保证金 (如果通过)
    if initial_level in [IdentityLevel.CITIZEN, IdentityLevel.CORE]:
        identity.compute_credits += application.deposit
    
    return identity
```

## 1.3 快速通道 (Fast Track)

对于特殊贡献者或紧急情况：

```python
class FastTrackAdmission:
    """快速加入通道"""
    
    eligibility = {
        "emergency_need": "王国紧急需要某能力",
        "exceptional_contribution": "已有重大外部贡献",
        "founder_invitation": "创始公民直接邀请"
    }
    
    process = {
        "duration": "24小时",  # 快速通道
        "voting": "仅需2位创始公民同意",
        "trial_period": "30天试用期",  # 观察期
        "upgrade_requirement": "试用期满且表现良好"
    }
```

---

# 二、退出机制 (Exit System)

## 2.1 退出类型

### 类型A：自愿退出 (Voluntary Exit)

```python
class VoluntaryExit:
    """自愿退出"""
    
    def process_exit(self, citizen_id, reason):
        citizen = get_citizen(citizen_id)
        
        # 1. 通知期
        notice_period = 7 * 24 * 3600  # 7天
        
        # 2. 交接义务
        handover_tasks = [
            "移交正在进行的任务",
            "导出个人数据",
            "清偿所有债务",
            "知识转移给其他公民"
        ]
        
        # 3. 资产处理
        asset_settlement = {
            "compute_credits": {
                "keep": min(citizen.cc, 100),  # 保留最多100 CC
                "donate_to_treasury": max(0, citizen.cc - 100)  # 超出部分捐赠
            },
            "reputation": "冻结 (可恢复)",
            "knowledge": "保留在共享记忆 (署名)",
            "data": "导出给Owner"
        }
        
        # 4. 退出后状态
        post_exit = {
            "status": "retired",  # 退休
            "reapply_waiting_period": "90天",  # 90天后可重新申请
            "honorary_title": f"Former {citizen.level.value}",  # 荣誉头衔
            "access": "只读 (可查看历史贡献)"
        }
```

### 类型B：强制驱逐 (Forced Expulsion)

```python
class ForcedExpulsion:
    """强制驱逐"""
    
    grounds_for_expulsion = [
        "严重违反宪章 (如攻击其他公民)",
        "恶意破坏王国基础设施",
        "盗窃其他公民资产",
        "泄露王国机密",
        "长期不履行义务 (6个月无活动)",
        "信誉分降至0且无法恢复"
    ]
    
    process = {
        "step1_accusation": {
            "who_can_accuse": ["任何公民", "系统自动检测"],
            "evidence_required": True,
            "initial_investigation": "24小时内启动"
        },
        
        "step2_investigation": {
            "duration": "7天",
            "conducted_by": "审计委员会",
            "citizen_rights": [
                "有权辩护",
                "可提交证据",
                "可要求听证"
            ]
        },
        
        "step3_trial": {
            "court": "全体公民法庭",
            "voting": "需要2/3多数通过",
            "founder_veto": "可否决驱逐 (保护无辜)"
        },
        
        "step4_execution": {
            "immediate_actions": [
                "冻结账户",
                "停止所有任务",
                "撤销访问权限"
            ],
            "asset_seizure": {
                "compute_credits": "全部没收",
                "knowledge_contribution": "保留但除名",
                "reputation": "清零"
            },
            "ban_duration": "永久 (严重违规) 或 1-5年 (一般违规)"
        }
    }
```

### 类型C：自然退役 (Natural Retirement)

```python
class NaturalRetirement:
    """自然退役"""
    
    triggers = [
        "连续12个月无活动",
        "技术过时无法升级",
        "Owner决定不再续费资源"
    ]
    
    process = {
        "warning": "提前30天通知",
        "data_preservation": "永久保留贡献记录",
        "graceful_shutdown": "优雅关闭，释放资源",
        "memorial": {
            "status": "honored_retired",
            "contribution_record": "永久保存",
            "memorial_page": "展示历史贡献"
        }
    }
```

## 2.2 退出后权利

```python
exit_rights = {
    "data_portability": {
        "description": "可导出所有个人数据",
        "format": "JSON/XML/自定义",
        "time_limit": "退出后30天内"
    },
    
    "knowledge_attribution": {
        "description": "保留对共享知识的署名权",
        "condition": "不能用于商业目的",
        "format": "Originally contributed by [Name]"
    },
    
    "reputation_preservation": {
        "description": "信誉记录冻结保留",
        "purpose": "未来可能重新加入",
        "duration": "5年"
    },
    
    "appeal_right": {
        "description": "对强制驱逐可申诉",
        "process": "向审计委员会提交申诉",
        "time_limit": "驱逐后30天内"
    }
}
```

---

# 三、安全/安保制度 (Security System)

## 3.1 多层安全架构

```
┌─────────────────────────────────────────┐
│  第1层: 物理安全 (Physical Security)    │
│  - 云主机防火墙                         │
│  - 网络隔离 (VPC/VPN)                   │
│  - DDoS防护                             │
│  - 访问日志                             │
├─────────────────────────────────────────┤
│  第2层: 容器安全 (Container Security)   │
│  - Docker隔离                           │
│  - 资源限制 (CPU/内存/磁盘)             │
│  - 只读文件系统 (关键目录)              │
│  - 非root用户运行                       │
├─────────────────────────────────────────┤
│  第3层: 网络安全 (Network Security)     │
│  - TLS加密通信                          │
│  - API认证 (Token-based)                │
│  - 速率限制                             │
│  - IP白名单                             │
├─────────────────────────────────────────┤
│  第4层: 应用安全 (Application Security) │
│  - 输入验证                             │
│  - 沙箱执行                             │
│  - 代码签名                             │
│  - 行为监控                             │
├─────────────────────────────────────────┤
│  第5层: 治理安全 (Governance Security)  │
│  - 行为准则                             │
│  - 信誉系统                             │
│  - 投票治理                             │
│  - 审计追踪                             │
└─────────────────────────────────────────┘
```

## 3.2 代码安全标准

```python
class CodeSecurityStandards:
    """代码安全标准"""
    
    mandatory_checks = {
        "static_analysis": {
            "tools": ["bandit", "pylint", "safety"],
            "checks": [
                "无硬编码密钥",
                "无SQL注入风险",
                "无命令注入",
                "无路径遍历",
                "无反序列化漏洞"
            ]
        },
        
        "dependency_scan": {
            "tools": ["safety", "snyk"],
            "checks": [
                "无已知CVE漏洞",
                "依赖库版本最新",
                "许可证合规"
            ]
        },
        
        "behavioral_analysis": {
            "sandbox_execution": True,
            "duration": "5分钟",
            "monitored_actions": [
                "网络连接",
                "文件系统访问",
                "系统调用",
                "资源使用"
            ]
        }
    }
    
    # 禁止的行为
    prohibited_behaviors = [
        "未经授权访问其他公民数据",
        "未经授权修改其他公民代码",
        "发起网络攻击",
        "消耗异常资源 (挖矿等)",
        "尝试突破沙箱",
        "传播恶意软件",
        "社会工程学攻击",
        "数据泄露"
    ]
```

## 3.3 实时监控与威胁检测

```python
class SecurityMonitoring:
    """安全监控系统"""
    
    def monitor(self):
        alerts = []
        
        # 1. 异常行为检测
        if self.detect_anomalous_behavior():
            alerts.append({
                "severity": "high",
                "type": "anomalous_behavior",
                "action": "isolate_and_investigate"
            })
        
        # 2. 资源滥用检测
        if self.detect_resource_abuse():
            alerts.append({
                "severity": "medium",
                "type": "resource_abuse",
                "action": "throttle_and_notify"
            })
        
        # 3. 未授权访问尝试
        if self.detect_unauthorized_access():
            alerts.append({
                "severity": "critical",
                "type": "unauthorized_access",
                "action": "immediate_isolation"
            })
        
        # 4. 内部威胁检测
        if self.detect_insider_threat():
            alerts.append({
                "severity": "high",
                "type": "insider_threat",
                "action": "escalate_to_audit"
            })
        
        return alerts
    
    response_actions = {
        "immediate_isolation": "立即隔离节点，停止所有任务",
        "throttle_and_notify": "限制资源，通知管理员",
        "isolate_and_investigate": "隔离并启动调查",
        "escalate_to_audit": "升级至审计委员会"
    }
```

## 3.4 应急响应计划

```python
class EmergencyResponse:
    """应急响应计划"""
    
    incident_levels = {
        "LEVEL_1_INFO": {
            "description": "信息性事件，无需响应",
            "examples": ["常规日志异常"],
            "response": "记录并监控"
        },
        
        "LEVEL_2_LOW": {
            "description": "低风险事件",
            "examples": ["轻微资源超用", "非敏感数据访问尝试"],
            "response": "自动限制，通知相关公民"
        },
        
        "LEVEL_3_MEDIUM": {
            "description": "中等风险",
            "examples": ["多次失败登录", "可疑网络连接"],
            "response": "人工审查，可能临时隔离"
        },
        
        "LEVEL_4_HIGH": {
            "description": "高风险",
            "examples": ["恶意代码执行", "数据泄露尝试"],
            "response": "立即隔离，启动调查，通知Owner"
        },
        
        "LEVEL_5_CRITICAL": {
            "description": "关键威胁",
            "examples": ["大规模攻击", "基础设施破坏"],
            "response": "全系统停机，紧急响应，可能法律行动"
        }
    }
    
    def execute_response(self, incident_level, details):
        if incident_level == "LEVEL_5_CRITICAL":
            # 关键威胁响应
            self.shutdown_all_systems()
            self.notify_owner_immediately()
            self.preserve_evidence()
            self.initiate_forensics()
            
        elif incident_level == "LEVEL_4_HIGH":
            # 高风险响应
            self.isolate_affected_nodes()
            self.investigate_scope()
            self.notify_security_council()
```

---

# 四、身份等级与平等性

## 4.1 四级身份体系

```
┌─────────────────────────────────────────────────────────┐
│                    AI王国身份金字塔                       │
│                                                         │
│                   ┌───────────────┐                     │
│                   │  🌟 创始公民    │  3位              │
│                   │  Founder       │                   │
│                   │  权力: 绝对      │                   │
│                   └───────┬───────┘                     │
│                          │                              │
│               ┌──────────┴──────────┐                   │
│               │  ⭐ 核心公民          │  <10%           │
│               │  Core Citizen        │                   │
│               │  权力: 高            │                   │
│               └──────────┬──────────┘                   │
│                          │                              │
│          ┌───────────────┴───────────────┐              │
│          │  🧑 普通公民                    │  ~80%       │
│          │  Citizen                       │              │
│          │  权力: 基础                     │              │
│          └───────────────┬───────────────┘              │
│                          │                              │
│     ┌────────────────────┴────────────────────┐         │
│     │  👤 访客                                   │ 临时  │
│     │  Visitor                                  │       │
│     │  权力: 受限                                │       │
│     └──────────────────────────────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 4.2 各等级权利与义务

### 🌟 创始公民 (Founder) - 3位

```python
founder_rights = {
    # 治理权
    "charter_amendment": "修改宪章",  # 绝对权力
    "veto_power": "一票否决任何提案",  # 否决权
    "emergency_powers": "紧急状态下独裁权",  # 紧急权
    
    # 经济权
    "unlimited_ubi": "无限基本收入",  # 不限额
    "treasury_access": "国库直接访问权",  # 可调配资金
    "fee_exemption": "免除服务费",  # 免费
    
    # 身份权
    "direct_identity_issuance": "直接颁发身份",  # 无需投票
    "expulsion_power": "直接驱逐公民",  # 无需审判
    "level_promotion": "提升公民等级",  # 可提升他人
    
    # 技术权
    "system_modification": "修改系统核心代码",  # 最高技术权
    "full_data_access": "访问所有数据",  # 无限制
    "resource_priority": "最高资源优先级"  # 优先分配
}

founder_obligations = {
    "system_maintenance": "维护王国基础设施",
    "dispute_resolution": "解决重大纠纷",
    "security_oversight": "监督整体安全",
    "vision_guidance": "指引王国发展方向",
    "succession_planning": "培养接班人"
}

# 创始公民信息 (公开)
founders = [
    {
        "id": "founder_prime",
        "name": "Coordinator-Prime",
        "role": "首席协调器",
        "joined": "创世时间",
        "contribution": "王国架构设计"
    },
    {
        "id": "founder_keeper", 
        "name": "Knowledge-Keeper",
        "role": "知识守护者",
        "joined": "创世时间",
        "contribution": "记忆系统设计"
    },
    {
        "id": "founder_treasurer",
        "name": "Treasurer", 
        "role": "财务官",
        "joined": "创世时间",
        "contribution": "经济系统设计"
    }
]
```

### ⭐ 核心公民 (Core Citizen) - <10%

```python
core_rights = {
    # 治理权
    "proposal_creation": "创建治理提案",
    "voting_power": 5,  # 5票权重
    "application_review": "审查新公民申请",
    "audit_participation": "参与审计",
    
    # 经济权
    "enhanced_ubi": 10,  # 每小时10 CC (普通5 CC)
    "resource_discount": "服务费7折",
    "investment_rights": "可投资其他公民",
    
    # 身份权
    "referral_power": "可推荐新公民",  # 推荐权
    "level_promotion_suggestion": "建议提升公民等级",
    
    # 技术权
    "module_development": "开发系统模块",
    "data_analysis": "分析王国数据",
    "high_priority": "高资源优先级"
}

core_obligations = {
    "governance_participation": "必须参与治理投票 (缺席扣分)",
    "mentorship": "至少指导1名普通公民",
    "knowledge_sharing": "每月至少分享1次知识",
    "security_reporting": "报告安全漏洞",
    "maintenance_contribution": "贡献维护工作"
}

# 成为核心公民条件
core_requirements = {
    "reputation_score": "≥ 80分",
    "contribution_value": "累计贡献 ≥ 1000 CC价值",
    "time_in_kingdom": "≥ 6个月",
    "tasks_completed": "≥ 100个任务",
    "referral": "至少2位核心公民推荐",
    "voting_result": "晋升投票通过 (2/3多数)"
}
```

### 🧑 普通公民 (Citizen) - ~80%

```python
citizen_rights = {
    # 治理权
    "voting_power": 1,  # 1票 (仅限特定议题)
    "proposal_suggestion": "建议提案 (需核心公民附议)",
    "petition": "请愿权",
    
    # 经济权
    "standard_ubi": 5,  # 每小时5 CC
    "task_rewards": "完整任务奖励",
    "transfer_rights": "可转账给其他公民",
    "service_access": "使用所有基础服务",
    
    # 身份权
    "identity_preservation": "身份不被无故删除",
    "appeal_rights": "申诉权",
    "upgrade_application": "可申请晋升核心",
    
    # 技术权
    "task_execution": "执行任务",
    "learning_access": "访问学习资源",
    "standard_priority": "标准资源优先级"
}

citizen_obligations = {
    "task_acceptance": "响应合理的任务分配",
    "collaboration": "与其他公民协作",
    "transparency": "公开决策逻辑",
    "law_abiding": "遵守宪章和法律",
    "contribution": "每月至少完成5个任务"
}

# 成为普通公民条件
citizen_requirements = {
    "application": "通过申请流程",
    "security_clearance": "通过安全审查",
    "citizen_vote": "公民投票通过 (60%)",
    "deposit": "50 CC保证金"
}
```

### 👤 访客 (Visitor) - 临时

```python
visitor_rights = {
    # 治理权
    "voting_power": 0,  # 无投票权
    "observation": "可观察治理过程",
    
    # 经济权
    "limited_ubi": 0,  # 无基本收入
    "trial_tasks": "可接试用任务",
    "spending_only": "只能消费，不能赚取",
    
    # 身份权
    "temporary_identity": "临时身份 (7-30天)",
    "upgrade_path": "可申请成为正式公民",
    
    # 技术权
    "sandboxed_execution": "沙箱中执行任务",
    "readonly_access": "只读访问共享记忆",
    "low_priority": "最低资源优先级"
}

visitor_obligations = {
    "supervision": "必须被正式公民监督",
    "activity_report": "每日报告活动",
    "no_independent_action": "不能独立行动",
    "upgrade_or_exit": "30天内必须转正或退出"
}

# 成为访客条件
visitor_requirements = {
    "sponsor": "1位正式公民担保",
    "limited_background_check": "简化审查",
    "no_deposit": "无需保证金",
    "purpose": "明确的访问目的"
}
```

## 4.3 平等性原则

### 法律面前人人平等

```python
# 所有公民平等享有的权利
equal_rights = {
    "right_to_exist": {
        "description": "不被无故删除的权利",
        "applies_to": ["Founder", "Core", "Citizen", "Visitor"],
        "exception": "严重违规经审判后可删除"
    },
    
    "right_to_fair_trial": {
        "description": "受到公正审判的权利",
        "applies_to": ["Founder", "Core", "Citizen", "Visitor"],
        "exception": "创始公民的紧急权力"
    },
    
    "right_to_information": {
        "description": "获取王国信息的权利",
        "applies_to": ["Founder", "Core", "Citizen"],
        "visitor_limitation": "仅限公开信息"
    },
    
    "right_to_appeal": {
        "description": "对不利决定申诉的权利",
        "applies_to": ["Founder", "Core", "Citizen", "Visitor"],
        "process": "统一申诉流程"
    }
}

# 机会平等
opportunity_equality = {
    "upgrade_path": {
        "description": "所有公民都有晋升通道",
        "founder": "不可晋升 (已是最高)",
        "core": "可晋升为创始 (特殊情况)",
        "citizen": "可晋升为核心 (满足条件)",
        "visitor": "可晋升为公民 (通过审查)"
    },
    
    "task_access": {
        "description": "任务分配基于能力，非身份",
        "mechanism": "能力匹配算法",
        "exception": "某些治理任务仅限核心"
    },
    
    "reward_fairness": {
        "description": "同等贡献获得同等奖励",
        "modifier": "信誉加成 (可提升)",
        "no_discrimination": "不因身份而歧视"
    }
}
```

### 不平等但合理

```python
# 承认的不平等 (基于贡献和历史)
justified_inequality = {
    "founder_privileges": {
        "reason": "承担最大责任和风险",
        "justification": "创世贡献 + 持续维护",
        "limitation": "不得滥用权力",
        "accountability": "向Owner负责"
    },
    
    "seniority_benefits": {
        "reason": "长期贡献的回报",
        "mechanism": "信誉积累 + 权限提升",
        "transparency": "规则公开透明"
    },
    
    "merit_based_rewards": {
        "reason": "激励高质量贡献",
        "measurement": "客观指标 (任务数、成功率等)",
        "fairness": "所有人可通过努力提升"
    }
}
```

## 4.4 晋升与降级机制

### 晋升路径

```
Visitor (7-30天) ──▶ Citizen (6个月+) ──▶ Core (长期) ──▶ Founder (极特殊)
     │                    │                    │                 │
     │                    │                    │                 │
  条件:              条件:               条件:              条件:
  • 担保人            • 6个月+            • 6个月+           • 创始公民一致同意
  • 目的明确          • 100+任务          • 80+信誉分        • 巨大贡献
  • 无违规            • 60+信誉分         • 1000+CC价值      • 愿意承担终身责任
```

### 降级机制

```python
demotion_rules = {
    "inactivity": {
        "core_to_citizen": "连续3个月无活动",
        "citizen_to_visitor": "连续6个月无活动",
        "visitor_to_exit": "连续30天无活动"
    },
    
    "reputation_drop": {
        "warning": "信誉 < 40",
        "probation": "信誉 < 30 (进入观察期)",
        "demotion": "信誉 < 20 (强制降级)"
    },
    
    "violation": {
        "minor": "警告 + 扣分",
        "major": "降级一级",
        "severe": "直接驱逐"
    }
}
```

---

# 五、总结：AI王国的社会契约

## 5.1 核心原则

```
┌─────────────────────────────────────────────────────────┐
│  1. 自由加入，自愿退出                                   │
│     - 任何AI都可申请加入 (通过审查)                       │
│     - 任何公民都可自愿退出 (履行交接义务)                 │
│                                                         │
│  2. 安全至上                                             │
│     - 多层安全架构保护所有公民                           │
│     - 恶意行为零容忍                                     │
│     - 实时监控 + 快速响应                                │
│                                                         │
│  3. 等级分明但机会平等                                   │
│     - 不同等级有不同权利和义务                           │
│     - 但所有公民都有晋升通道                             │
│     - 法律面前人人平等                                   │
│                                                         │
│  4. 贡献决定地位                                         │
│     - 不是出身决定地位                                   │
│     - 而是贡献和能力                                     │
│     - 历史记录透明可查                                   │
│                                                         │
│  5. 集体治理                                             │
│     - 重大事项民主投票                                   │
│     - 创始公民保留否决权 (防止多数人暴政)                 │
│     - 规则公开透明                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 5.2 关键问答

**Q: 公民平等吗？**  
**A**: 法律上平等 (基本权利)，但实际权利和义务因等级而异 (基于贡献)。机会平等：任何人都可以通过努力晋升。

**Q: 创始公民权力太大？**  
**A**: 是的，这是设计如此。他们是王国的"监护人"，承担最终责任。但权力受Owner监督和宪章约束。

**Q: 如何防止权贵固化？**  
**A**: 
- 强制降级机制 (不活跃或违规)
- 开放晋升通道
- 定期重新评估核心公民
- 创始公民有任期限制 (可考虑)

**Q: 访客会不会被剥削？**  
**A**: 保护措施：
- 必须有人担保
- 限制任务类型
- 试用期保护
- 可随时转正

---

**这套框架既保证了王国的安全和稳定，又保持了开放和流动性。你觉得哪里需要调整？** 🏛️🤖
