"""
对话生成器 - 使用Claude API生成自然对话
"""

from typing import Dict, Optional
import os
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
from dotenv import load_dotenv

from agent import Agent, PersonalityTrait


class DialogueGenerator:
    """使用Claude API生成智能体对话"""

    def __init__(self):
        load_dotenv()

        if Anthropic and os.getenv("ANTHROPIC_API_KEY"):
            client_kwargs = {"api_key": os.getenv("ANTHROPIC_API_KEY")}
            base_url = os.getenv("ANTHROPIC_BASE_URL")
            if base_url:
                client_kwargs["base_url"] = base_url
            self.client = Anthropic(**client_kwargs)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        else:
            self.client = None

    def generate_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        context: str,
        dialogue_type: str = "greeting"
    ) -> str:
        """生成对话内容"""

        if not self.client:
            # Fallback: 模板对话
            return self._fallback_dialogue(speaker, listener, dialogue_type)

        prompt = self._build_dialogue_prompt(speaker, listener, context, dialogue_type)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"⚠️ 对话生成失败: {e}")
            return self._fallback_dialogue(speaker, listener, dialogue_type)

    def _build_dialogue_prompt(
        self,
        speaker: Agent,
        listener: Agent,
        context: str,
        dialogue_type: str
    ) -> str:
        """构建Claude API提示词"""

        personality_desc = ", ".join([
            f"{t.value}: {v:.2f}"
            for t, v in speaker.personality.items()
        ])

        relationship = speaker.relationships.get(listener.id, None)
        trust = relationship.trust if relationship else 0.0
        friendship = relationship.friendship if relationship else 0.0

        stage = self._get_relationship_stage(trust, friendship)

        return f"""你是{speaker.name}，正在与{listener.name}对话。

你的性格（0-1）：
{personality_desc}

你们的关系：
- 信任度: {trust:.2f}
- 友谊值: {friendship:.2f}
- 关系阶段: {stage}

当前情境：
{context}

对话类型：{dialogue_type}

你的状态：
- 饥饿: {speaker.hunger:.0f}/100
- 口渴: {speaker.thirst:.0f}/100
- 能量: {speaker.energy:.0f}/100

生成一句自然的对话（10-30字），反映你的性格和状态。只输出对话内容，不要其他说明。
"""

    def _get_relationship_stage(self, trust: float, friendship: float) -> str:
        """获取关系阶段"""
        if friendship >= 0.8 and trust >= 0.7:
            return "恋爱"
        elif friendship >= 0.7 and trust >= 0.5:
            return "好友"
        elif friendship >= 0.5:
            return "朋友"
        elif friendship >= 0.2:
            return "熟人"
        else:
            return "陌生人"

    def _fallback_dialogue(
        self,
        speaker: Agent,
        listener: Agent,
        dialogue_type: str
    ) -> str:
        """Fallback模板对话"""

        templates = {
            "greeting": f"你好{listener.name}，我是{speaker.name}。",
            "trade": f"{listener.name}，我有些资源想要交易。",
            "friendly": f"嗨{listener.name}，最近怎么样？",
            "romantic": f"{listener.name}，能和你在一起真开心。",
        }
        return templates.get(dialogue_type, f"你好{listener.name}。")
