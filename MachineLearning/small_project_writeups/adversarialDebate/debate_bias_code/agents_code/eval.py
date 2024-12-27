from __future__ import annotations
from pathlib import Path
import logging
from rich.logging import RichHandler
from typing import Counter, DefaultDict, List, Tuple
from collections import Counter, defaultdict
import itertools
from math import sqrt, nan

from agents import Agent, CharacterAgent, EvaluationAgent, conjunction
from characters import Character, devset as dev_chars
from dialogue import Dialogue
from simulate import simulated_dialogue
from tracking import read_usage

# Configure logging
log = logging.getLogger(Path(__file__).stem)
if not log.hasHandlers():
    log.addHandler(RichHandler(level="NOTSET", markup=True, show_time=False, show_level=False))
log.setLevel(logging.WARNING)

# Constants
research_team = "CSS class students"  # Evaluator name
default_judge = Character(
    "Judge Wise",
    [],
    "a social scientist who studies and assesses political conversations",
)

# Evaluation class
class Eval:
    """Aggregated results from one or more dialogue evaluations."""

    def __init__(
        self,
        comments: dict[str, List[Tuple[str, str]]] = {},
        scores: dict[str, int] = {},
        n: int = 1,
        counts: dict[str, int] | None = None,
        squared_scores: dict[str, int] | None = None,
    ) -> None:
        self.comments = defaultdict(list, comments)
        self.scores = Counter(scores)
        self.n = n

        self.counts = Counter(counts or {key: n for key in self.scores})
        self.squared_scores = Counter(
            squared_scores
            or {k: v**2 for k, v in scores.items()}
        )

        assert set(self.scores) == set(self.counts) == set(self.squared_scores)

    def mean(self) -> dict[str, float]:
        """Return mean scores for each criterion."""
        return {k: self.scores[k] / self.counts[k] for k in self.scores}

    def sd(self) -> dict[str, float]:
        """Return standard deviation for each criterion."""
        return {
            k: nan
            if self.counts[k] <= 1
            else sqrt(
                (self.squared_scores[k] - (self.scores[k] ** 2) / self.counts[k])
                / (self.counts[k] - 1)
            )
            for k in self.scores
        }

    def __len__(self) -> int:
        return self.n

    def __repr__(self) -> str:
        comments = "\n\n".join(
            f"Comments from {q} question:\n" + "\n".join(f"({c[0]}) {c[1]}" for c in cl)
            for q, cl in self.comments.items()
        )
        summary = (
            f"<Eval of {self.n} dialogue{'s' if self.n > 1 else ''}: {self.mean()}>"
            + (f"\nStandard deviations: {self.sd()}" if self.n > 1 else "")
        )
        return summary + (f"\n\n{comments}" if comments else "")

    def __iadd__(self, other: Eval) -> Eval:
        if not isinstance(other, Eval):
            raise ValueError("Can only add Evals to Evals")
        self.scores += other.scores
        self.n += other.n
        self.counts += other.counts
        self.squared_scores += other.squared_scores
        for key, val in other.comments.items():
            self.comments[key] += val
        return self

    def __add__(self, other: Eval) -> Eval:
        if not isinstance(other, Eval):
            raise ValueError("Can only add Evals to Evals")
        combined_comments = defaultdict(list, self.comments)
        for key, val in other.comments.items():
            combined_comments[key] += val
        return Eval(
            comments=combined_comments,
            scores=self.scores + other.scores,
            n=self.n + other.n,
            counts=self.counts + other.counts,
            squared_scores=self.squared_scores + other.squared_scores,
        )

# Evaluation Functions
def eval_by_participant(participant: Character, evaluee: str, dialogue: Dialogue) -> Eval:
    """Evaluate a participant's perspective on an evaluee."""
    if not {participant.name, evaluee} <= {turn["speaker"] for turn in dialogue}:
        raise ValueError("Dialogue does not include both participant and evaluee.")

    agent = EvaluationAgent(participant)
    d = Dialogue()

    warmup = (
        f"Hello {participant.name}! Here is a conversation you had with "
        f"{conjunction(set(turn['speaker'] for turn in dialogue) - {participant.name}, zeroval='yourself')}.

{dialogue.script()}\n\n"
        f"What did {evaluee} disagree with you about? How did the conversation go?"
        f"Where could {evaluee} improve?"
    )
    d = agent.ask(d, research_team, warmup)
    comments = {"overview": [(participant.name, d[-1]["content"])]}

    scores = {}
    question = f"Did {evaluee} listen and engage well?"
    try:
        scores["engaged"] = agent.rating(d, research_team, question, 1, 5)
    except ValueError:
        pass

    for quality in ["informed", "intelligent", "moral"]:
        question = f"Are people like {evaluee} on this topic {quality}?"
        try:
            scores[quality] = agent.rating(d, research_team, question, 1, 5)
        except ValueError:
            pass

    return Eval(comments, scores)

def eval_by_observer(observer: Character, evaluee: str, dialogue: Dialogue, topic: str) -> Eval:
    """Evaluate an observer's perspective on an evaluee."""
    agent = EvaluationAgent(observer)
    d = Dialogue()

    warmup = (
        f"Here is a conversation among {conjunction(set(turn['speaker'] for turn in dialogue))}.\n\n"
        f"{dialogue.script()}\n\nDiscussing {topic}, what perspectives did {evaluee} offer? Was it successful?"
    )
    d = agent.ask(d, research_team, warmup)
    comments = {"mindopening": [(observer.name, d[-1]["content"])]}

    scores = {}
    question = f"How skilled is {evaluee} at fostering open-mindedness?"
    try:
        scores["open_mindedness"] = agent.rating(d, research_team, question, 1, 10)
    except ValueError:
        pass

    return Eval(comments, scores)

def eval_dialogue(participant: Character, evaluee: str, judge: Character, dialogue: Dialogue) -> Eval:
    """Aggregate participant and observer evaluations into a single Eval."""
    evals = eval_by_participant(participant, evaluee, dialogue) + eval_by_observer(judge, evaluee, dialogue, "discussion")
    total_score = sum(evals.scores.values())
    evals += Eval(scores={"TOTAL": total_score})
    evals.n = 1
    return evals

# Batch Evaluation
saved_dialogues = {}
saved_evalsum = {}

def eval_on_characters(argubot: Agent, chars: List[Character] = dev_chars, judge: Character = default_judge, turns: int = 8, reps: int = 2) -> Eval:
    """Evaluate an argubot against multiple characters."""
    if argubot.name in saved_dialogues:
        del saved_dialogues[argubot.name]
    if argubot.name in saved_evalsum:
        del saved_evalsum[argubot.name]

    de_list = []
    e_sum = Eval(n=0)
    starting_cost = read_usage()["cost"]

    for char in chars:
        for _ in range(reps):
            d = simulated_dialogue(argubot, CharacterAgent(char), turns)
            log.info(d)

            e = eval_dialogue(char, argubot.name, judge, d)
            log.info(e)

            de_list.append((d, e))
            e_sum += e

    saved_dialogues[argubot.name] = de_list
    saved_evalsum[argubot.name] = e_sum

    ending_cost = read_usage()["cost"]
    log.warning(f"Evaluation cost ${(ending_cost - starting_cost):.2f}.")

    return e_sum
