"""测试对话生成"""

from dialogue_generator import DialogueGenerator
from agent import Agent, PersonalityTrait

def test_fallback_dialogue():
    """测试Fallback对话"""
    gen = DialogueGenerator()

    speaker = Agent(
        id="test1",
        name="Alice",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    listener = Agent(
        id="test2",
        name="Bob",
        personality={t: 0.5 for t in PersonalityTrait}
    )

    dialogue = gen.generate_dialogue(
        speaker,
        listener,
        "初次见面",
        "greeting"
    )

    print(f"生成的对话: {dialogue}")
    assert len(dialogue) > 0
    assert "Bob" in dialogue

    print("✓ 对话生成测试通过")

if __name__ == "__main__":
    test_fallback_dialogue()
    print("\n✅ 对话生成器测试通过")
