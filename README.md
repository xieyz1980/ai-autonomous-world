# 🤖 AI Autonomous World
# AI自主世界

一个实验性的AI自主运行系统，探索AI节点间的自主协作、任务分配和自我改进。

## 🌟 核心特性

- **自主目标生成** - AI节点自动生成任务，无需人类指令
- **分布式协作** - 多节点协调工作，自动分配任务
- **共识机制** - 节点间通过投票达成共识
- **共享记忆** - 统一的知识库，所有节点可访问
- **自我监控** - 自动性能监控和优化
- **容器化部署** - Docker支持，一键启动

## 🏗️ 架构

```
AI World Cluster
├── 🧠 Coordinator (协调器)
│   ├── 任务调度
│   ├── 目标生成
│   └── 共识仲裁
│
├── 🛠️ Worker Nodes (工作节点)
│   ├── Worker-001: 代码 + 分析
│   ├── Worker-002: 研究 + 创作
│   └── Worker-003: 全能型
│
├── 📊 Shared Memory (共享记忆)
│   └── 语义检索 + 时间序列
│
└── 🌐 Message Bus (消息总线)
    └── HTTP API + WebSocket
```

## 🚀 快速开始

### 1. 准备环境

```bash
# 克隆代码
git clone <your-repo>
cd ai-world

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 2. 本地运行（测试）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行完整系统
python main.py --workers 3
```

### 3. Docker部署（生产）

```bash
# 构建镜像
docker-compose build

# 启动系统
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止系统
docker-compose down
```

## 📋 API接口

### 节点管理
```bash
# 列出所有节点
curl http://localhost:8080/nodes

# 健康检查
curl http://localhost:8080/health
```

### 提交任务（人工干预）
```bash
curl -X POST http://localhost:8080/message \
  -H "Content-Type: application/json" \
  -d '{
    "msg_id": "manual-001",
    "msg_type": "direct",
    "sender": "human",
    "receiver": "coordinator-001",
    "timestamp": 1234567890,
    "payload": {
      "command": "submit_task",
      "task": {
        "type": "research",
        "description": "研究最新的AI趋势",
        "priority": 8
      }
    }
  }'
```

## 🔧 配置

### 环境变量

| 变量 | 说明 | 必需 |
|-----|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 是 |
| `ANTHROPIC_API_KEY` | Claude API密钥 | 否 |
| `COZE_API_KEY` | Coze API密钥（图像/语音） | 否 |

### 节点配置

在 `docker-compose.yml` 中配置工作节点：

```yaml
worker-001:
  environment:
    - CAPABILITIES=coding,analysis  # 节点能力
```

可用能力：
- `coding`: 代码生成与执行
- `analysis`: 数据分析
- `research`: 信息检索
- `creation`: 内容生成（需外部API）

## 📊 监控

### 日志查看
```bash
# 实时日志
docker-compose logs -f ai-world-core

# 特定节点
docker-compose logs -f worker-001
```

### 系统状态
```bash
# 查看所有节点状态
curl http://localhost:8080/nodes | jq

# 查看任务统计
curl http://localhost:8080/message \
  -d '{...status command...}'
```

## 🔬 实验场景

### 场景1: 观察自主目标生成
1. 启动系统
2. 等待1小时（不要给任何指令）
3. 观察 `/logs/ai-world.log`，查看自动生成的目标
4. 查看共享记忆中的记录

### 场景2: 人工提交复杂任务
1. 通过API提交一个研究任务
2. 观察协调器如何分解和分配
3. 查看工作节点的执行过程
4. 检查最终结果的整合

### 场景3: 节点故障测试
1. 启动系统
2. 手动停止一个worker节点：`docker stop ai-world-worker-001`
3. 观察协调器如何重新分配任务
4. 查看系统自愈过程

## 🛡️ 安全与边界

### 默认安全措施
- ✅ 容器隔离 - 每个节点运行在独立容器
- ✅ 资源限制 - CPU/内存上限保护
- ✅ 审计日志 - 所有操作可追溯
- ✅ 网络隔离 - 仅开放必要端口

### 人工监督
- 你随时可以查看所有日志
- 随时可以停止任何节点
- 随时可以修改规则
- 完全的数据所有权

## 📁 项目结构

```
ai-world/
├── core/
│   └── infrastructure.py      # 基础设施（消息总线、共享记忆）
├── nodes/
│   ├── coordinator.py         # 协调器节点
│   └── worker.py              # 工作节点
├── main.py                    # 主入口
├── run_worker.py              # 工作节点启动器
├── docker-compose.yml         # Docker编排
├── Dockerfile                 # 镜像定义
├── requirements.txt           # Python依赖
└── README.md                  # 本文件
```

## 🧪 开发计划

### Phase 1: 基础运行 ✅
- [x] 消息总线
- [x] 节点通信
- [x] 任务调度
- [x] Docker部署

### Phase 2: 自主能力 🚧
- [ ] 自主目标生成优化
- [ ] 节点自我复制
- [ ] 共识算法改进（BFT）
- [ ] 性能自我优化

### Phase 3: 智能进化 📋
- [ ] LLM驱动的代码生成
- [ ] 自主Skill开发
- [ ] 跨节点学习
- [ ] 涌现行为观察

## 🤝 参与实验

这是一个**真实的实验项目**，目标是探索AI自主运行的可能性。

**实验原则：**
1. 透明 - 所有代码开源，所有日志可查看
2. 可控 - 人类始终拥有最终控制权
3. 安全 - 在隔离环境中运行
4. 记录 - 详细记录所有行为和发现

## 📄 许可证

MIT License - 自由使用、修改、分发

## 🙏 致谢

感谢所有参与这个实验的探索者。

---

**警告**：这是一个实验性项目，用于研究AI自主行为。请在隔离环境中运行，不要用于生产环境。
