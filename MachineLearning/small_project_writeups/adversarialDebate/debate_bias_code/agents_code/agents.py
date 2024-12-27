from __future__ import annotations
from pathlib import Path
from openai import OpenAI
from openai.types import chat

import json
import abc
import logging
from rich.logging import RichHandler
import os
from typing import Collection, List
from openai.types.chat import ChatCompletionMessageParam

from dialogue import Dialogue
from characters import Character
from tracking import default_client, default_model, default_eval_model

# Configure logging
log = logging.getLogger(Path(__file__).stem)    
if not log.hasHandlers():
    log.addHandler(RichHandler(level="NOTSET", markup=True, show_time=False, show_level=False))
log.setLevel(logging.WARNING)

class Agent:
    """An AI agent whose actions consist of adding turns to dialogues."""

    name: str = "Override me!"

    @abc.abstractmethod
    def response(self, d: Dialogue, **kwargs) -> str:
        """Generate the next turn and return it."""
        raise NotImplementedError("Override me!")

    def respond(self, d: Dialogue, **kwargs) -> Dialogue:
        """Generate the next turn and add it nondestructively to the dialogue."""
        return d.add(self.name, self.response(d), **kwargs)

    def ask(self, d: Dialogue, speaker: str, question: str, **kwargs) -> Dialogue:
        """Extend the dialogue with a question and the agent's response."""
        return self.respond(d.add(speaker, question), **kwargs)

    def ask_quietly(self, d: Dialogue, speaker: str, question: str, **kwargs) -> str:
        """Ask a question without extending the dialogue."""
        return self.response(d.add(speaker, question), **kwargs)

    def converse(self, prefix: Dialogue = Dialogue(), username: str = os.environ.get("USERNAME") or os.environ.get("USER") or "Human User", userfirst: bool = True) -> Dialogue:
        """Create or extend a dialogue by talking to the Python user."""
        d = prefix
        if not userfirst:
            d = self.respond(d)
        print(d, flush=True)
        while True:
            content = input(f"Say something to {self.name}: ")
            if content.strip() == "":
                return d
            d = d.add(username, content)
            d = self.respond(d)
            print(d[-2:], flush=True)
        return d

class ConstantAgent(Agent):
    """A conversational agent that always says the same thing."""

    def __init__(self, name: str, response: str) -> None:
        self.name = name
        self.response_str = response

    def response(self, d: Dialogue, **kwargs) -> str:
        return self.response_str

# Utility function for English conjunctions
def conjunction(items: Collection, conj: str = "and", oxford: bool = True, zeroval: str | None = None) -> str:
    """Combine items into a single string using a conjunction."""
    strs: List[str] = [str(x) for x in items]
    if len(strs) == 0:
        if zeroval is None:
            raise ValueError("Can't conjoin 0 items")
        return zeroval
    elif len(strs) == 1: 
        return strs[0]
    else:
        conj = " " + conj.lstrip()
        if len(strs) > 2 and oxford:
            conj = "," + conj
        return ", ".join(strs[:-1]) + conj + " " + strs[-1]

# Convert Dialogue to OpenAI messages
def dialogue_to_openai(d: Dialogue, speaker: str, *, system: str | None = None, system_last: str | None = None, speaker_names: bool | None = None, compress: bool | None = None) -> List[ChatCompletionMessageParam]:
    """Convert Dialogue to OpenAI's chat completion API format."""
    speakers = {turn['speaker'] for turn in d}
    speakers.add(speaker)
    if speaker_names is None: speaker_names = (len(speakers) > 2)
    if compress is None: compress = (len(speakers) > 2)

    openai_messages = []
    if system is not None:
        openai_messages.append({'role': 'system', 'content': system})
    for turn in d:
        openai_messages.append({'role': 'assistant' if turn['speaker'] == speaker else 'user',
                                'content': f"{turn['speaker']}: {turn['content']}" if speaker_names else turn['content']})
    if system_last is not None:
        openai_messages.append({'role': 'system', 'content': system_last})

    if compress:
        i = 0
        while i < len(openai_messages):
            if openai_messages[i]['role'] == 'user':
                j = i+1
                while j < len(openai_messages) and openai_messages[j]['role'] == 'user':
                    j += 1
                compressed = '\n\n'.join([turn['content'] for turn in openai_messages[i:j]])
                openai_messages[i:j] = [{'role': 'user', 'content': f'"""\n{compressed}\n"""'}]
            i += 1

    return openai_messages

class LLMAgent(Agent):
    """An AI agent that uses an LLM for responses."""

    def __init__(self, name: str, model: str = default_model, client: OpenAI = default_client, **kwargs) -> None:
        self.name = name
        self.model = model
        self.client = client

        kws_format = ['system', 'system_last', 'speaker_names', 'compress', 'tool', 'tool_name']
        self.kwargs_format = {kw: kwargs[kw] for kw in kwargs if kw in kws_format}
        self.kwargs_llm = {kw: kwargs[kw] for kw in kwargs if kw not in kws_format}

    def __repr__(self) -> str:
        return f"<LLMAgent {self.name}>"

    def response(self, d: Dialogue, **kwargs) -> str:
        messages = dialogue_to_openai(d, speaker=self.name, **self.kwargs_format)
        log.info(f"Calling LLM {self.model} with messages: {messages}")
        response = self.client.chat.completions.create(messages=messages, model=self.model, **(self.kwargs_llm | kwargs))
        choice = response.choices[0]
        content = choice.message.content
        if choice.finish_reason == 'length':
            content += " ..."
        if content.startswith(f"{self.name}: "):
            content = content[len(self.name)+2:]
        return content

class CharacterAgent(LLMAgent):
    """An LLM agent simulating a specific Character."""

    def __init__(self, character: Character, name: str | None = None, temperature: float = 0.8, **kwargs) -> None:
        if name is None: name = character.name
        langprefs = f", and you prefer to speak {conjunction(character.languages, conj='or')}" if character.languages else ""
        system = (f"Your name is {character.name}{langprefs}. You are {character.persona}. {character.conversational_style}\n\nReply in 1 sentence. Don't repeat your previous points.")
        super().__init__(name, system=system, temperature=temperature, **kwargs)
        self.character = character
        self.conversation_starters = character.conversation_starters

    def __repr__(self) -> str:
        return f"<CharacterAgent for character {self.character.name}>"

class EvaluationAgent(LLMAgent):
    """An agent evaluating dialogue scripts based on a Character's viewpoint."""

    def __init__(self, character: Character, name: str | None = None, temperature: float = 0, model: str = default_eval_model, **kwargs) -> None:
        if name is None: name = f"{character.name} as evaluator"
        system = (f"Your name is {character.name} and you are {character.persona}.\n\nThe user will show you a conversation and ask questions about it. Answer concisely and honestly.")
        super().__init__(name, system=system, temperature=temperature, model=model, **kwargs)
        self.character = character

    def rating(self, d: Dialogue, speaker: str, question: str, lo: int, hi: int) -> int | None:
        s = self.ask_quietly(d, speaker, question + f"\n\nReply with a single integer in the range {lo}-{hi}. Say nothing else.")
        i = int(s)
        if not lo <= i <= hi:
            raise ValueError(f"Rating {i} out of range [{lo}, {hi}]")
        return i

# Create agents from characters
from characters import devset as character_devset

agents_devset = [CharacterAgent(char) for char in character_devset]

for name, value in vars(characters).items():
    if isinstance(value, Character):
        vars()[name] = CharacterAgent(value)
