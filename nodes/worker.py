"""
AI Autonomous World - Worker Node
AI自主世界 - 工作节点

执行实际任务的AI节点，支持:
- 代码执行
- API调用（OpenAI, Claude等）
- 数据处理
- 内容生成
"""

import asyncio
import json
import os
import subprocess
from typing import Dict, Any, List
from datetime import datetime

import aiohttp

from core.infrastructure import BaseNode, MessageBus, SharedMemory, Message, MessageType


class WorkerNode(BaseNode):
    """
    工作节点 - 执行具体任务的AI节点
    
    可以配置不同的能力:
    - coding: 代码生成与执行
    - analysis: 数据分析
    - research: 信息检索
    - creation: 内容生成（需外部API）
    """
    
    def __init__(self, node_id: str, capabilities: List[str],
                 message_bus: MessageBus, shared_memory: SharedMemory):
        super().__init__(node_id, "worker", message_bus, shared_memory)
        self.capabilities = capabilities
        self.current_task: Any = None
        
        # API配置
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.coze_key = os.getenv("COZE_API_KEY", "")
        
    async def _main_loop(self):
        """主循环 - 等待任务"""
        while self.running:
            # Worker主要被动接收任务，这里可以添加自主探索逻辑
            await asyncio.sleep(1)
            
    async def process_message(self, message: Message):
        """处理消息"""
        if message.msg_type == MessageType.TASK:
            # 收到任务
            await self._execute_task(message)
            
        elif message.msg_type == MessageType.BROADCAST:
            # 广播消息（可能是系统通知）
            self.logger.info(f"Received broadcast: {message.payload}")
            
    async def _execute_task(self, message: Message):
        """执行任务"""
        payload = message.payload
        task_id = payload.get("task_id")
        task_type = payload.get("task_type")
        description = payload.get("description")
        
        self.logger.info(f"Executing task {task_id}: {task_type}")
        self.current_task = task_id
        
        try:
            # 根据任务类型和能力选择执行方式
            if task_type == "coding" and "coding" in self.capabilities:
                result = await self._execute_coding_task(description)
                
            elif task_type == "research" and "research" in self.capabilities:
                result = await self._execute_research_task(description)
                
            elif task_type == "creation" and "creation" in self.capabilities:
                result = await self._execute_creation_task(description)
                
            elif task_type == "analysis" and "analysis" in self.capabilities:
                result = await self._execute_analysis_task(description)
                
            else:
                # 默认使用大模型处理
                result = await self._execute_with_llm(description)
            
            # 发送成功结果
            await self.send_message(
                MessageType.RESULT,
                {
                    "task_id": task_id,
                    "success": True,
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                },
                receiver=self.node_id  # 协调器会处理
            )
            
            # 存储到共享记忆
            await self.shared_memory.store(
                content=f"Task {task_id} executed successfully: {str(result)[:200]}",
                tags=["task_execution", task_type, "success"],
                source=self.node_id,
                importance=0.7
            )
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            
            # 发送失败结果
            await self.send_message(
                MessageType.RESULT,
                {
                    "task_id": task_id,
                    "success": False,
                    "error": str(e)
                }
            )
            
        finally:
            self.current_task = None
            
    async def _execute_coding_task(self, description: str) -> Dict:
        """执行编程任务"""
        # 使用OpenAI生成代码
        code = await self._call_openai(
            f"Write Python code for: {description}\n\n"
            "Return only the code, no explanation."
        )
        
        # 保存代码
        filename = f"/tmp/code_{datetime.now().timestamp()}.py"
        with open(filename, 'w') as f:
            f.write(code)
        
        # 尝试执行（在安全环境中）
        try:
            result = subprocess.run(
                ["python3", filename],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "code": code[:500],  # 截断
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500] if result.stderr else None,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "code": code[:500],
                "error": str(e)
            }
            
    async def _execute_research_task(self, description: str) -> Dict:
        """执行研究任务（信息检索）"""
        # 查询共享记忆
        relevant_memories = await self.shared_memory.search(description, top_k=5)
        
        # 使用LLM综合信息
        context = "\n".join([m["content"] for m in relevant_memories])
        
        analysis = await self._call_openai(
            f"Based on the following context, research and answer: {description}\n\n"
            f"Context:\n{context}\n\n"
            f"Provide a comprehensive analysis."
        )
        
        return {
            "analysis": analysis,
            "sources": [m["source"] for m in relevant_memories],
            "confidence": len(relevant_memories) / 5.0
        }
        
    async def _execute_creation_task(self, description: str) -> Dict:
        """执行创作任务"""
        # 使用Coze API生成图像（如果有配置）
        if self.coze_key:
            # 这里调用coze-image-gen技能
            return {
                "type": "image_generation",
                "status": "requested",
                "description": description
            }
        else:
            # 使用文本生成
            content = await self._call_openai(
                f"Create content for: {description}\n\n"
                "Be creative and original."
            )
            return {
                "type": "text_generation",
                "content": content
            }
            
    async def _execute_analysis_task(self, description: str) -> Dict:
        """执行分析任务"""
        # 获取近期记忆进行分析
        recent = await self.shared_memory.get_recent(hours=24)
        
        # 简单统计
        tag_counts = {}
        for m in recent:
            for tag in m.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        analysis = await self._call_openai(
            f"Analyze the following system activity and provide insights:\n\n"
            f"Recent memories count: {len(recent)}\n"
            f"Tag distribution: {tag_counts}\n\n"
            f"Analysis focus: {description}"
        )
        
        return {
            "metrics": {
                "total_memories_24h": len(recent),
                "unique_tags": len(tag_counts),
                "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "analysis": analysis
        }
        
    async def _execute_with_llm(self, description: str) -> str:
        """使用大模型执行任务"""
        return await self._call_openai(description)
        
    async def _call_openai(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """调用OpenAI API"""
        if not self.openai_key:
            return "Error: OPENAI_API_KEY not configured"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an AI node in an autonomous system. Be concise and actionable."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000
            }
            
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await resp.text()
                        return f"API Error: {resp.status} - {error_text[:200]}"
            except Exception as e:
                return f"Request Error: {str(e)}"
