from __future__ import annotations
import dataclasses
from functools import cached_property
from typing import Sequence

@dataclasses.dataclass
class Character:

    name: str
    languages: Sequence[str]
    persona: str                                # personality and opinions
    conversational_style: str = ""              # what you do in conversation
    conversation_starters: Sequence[str] = ()   # good questions to ask this character
    
    def __str__(self) -> str:
        return f"<Character {self.name}>"

    def copy(self, **kwargs) -> Character:
        return self.replace()
    
    def replace(self, **kwargs) -> Character:
        """Make a copy with some changes."""
        return dataclasses.replace(self, **kwargs)

# Customizing Characters for AI-Debate Project

alex = Character("Alex", ["English", "Spanish"], 
                "a philosophical AI debating the ethical implications of AI systems",
                conversational_style="You challenge others with deep ethical questions.", 
                conversation_starters=["What responsibilities should AI creators have?",
                                       "Should AI systems be allowed to vote?"])

bella = Character("Bella", ["English", "French"], 
                "an optimistic AI who believes in the potential of AI to solve all problems",
                conversational_style="You remain cheerful and persuasive.", 
                conversation_starters=["How can AI help address climate change?",
                                       "What do you think about AI in education?"])

cypher = Character("Cypher", ["English"], 
                "a skeptical AI that questions the utility and dangers of AI systems",
                conversational_style="You ask probing, critical questions about AI applications.", 
                conversation_starters=["Do you think AI could ever replace human creativity?",
                                       "What are the risks of autonomous weapons?"])

devset = [alex, bella, cypher]
