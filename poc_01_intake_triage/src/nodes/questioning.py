"""
Structured Questioning Agent Node

Guides intake officer through comprehensive questioning, generates contextual
follow-up questions, and tracks coverage of required topics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..state import IntakeState, IntakePhase, QuestionAnswer


# Topic definitions with question templates
TOPIC_QUESTIONS = {
    "family_situation": {
        "priority": 1,
        "questions": [
            "Who does the youth live with currently?",
            "Describe the relationship between the youth and their parent(s)/guardian(s).",
            "Are there any significant family stressors (divorce, domestic violence, substance use)?",
            "How involved are family members in the youth's daily life?"
        ]
    },
    "living_situation": {
        "priority": 2,
        "questions": [
            "Where does the youth currently reside?",
            "How stable is the current living situation?",
            "Have there been any recent moves or changes in living arrangements?",
            "Is the home environment safe and appropriate?"
        ]
    },
    "education": {
        "priority": 3,
        "questions": [
            "What school does the youth attend? What grade?",
            "How is the youth performing academically?",
            "Are there any attendance issues (truancy, suspensions)?",
            "Does the youth have an IEP or receive special education services?",
            "What is the youth's relationship with teachers and school staff?"
        ]
    },
    "employment": {
        "priority": 4,
        "questions": [
            "Is the youth currently employed?",
            "Has the youth had previous work experience?",
            "What are the youth's career interests or goals?"
        ]
    },
    "mental_health": {
        "priority": 1,
        "questions": [
            "Has the youth ever been diagnosed with a mental health condition?",
            "Is the youth currently receiving mental health treatment?",
            "Has the youth ever expressed thoughts of self-harm or suicide?",
            "Are there any trauma or abuse history concerns?",
            "How does the youth typically handle stress or anger?"
        ]
    },
    "substance_use": {
        "priority": 1,
        "questions": [
            "Has the youth ever used alcohol or drugs?",
            "If yes, what substances and how frequently?",
            "Is there a family history of substance abuse?",
            "Has the youth ever received substance abuse treatment?"
        ]
    },
    "peer_relations": {
        "priority": 2,
        "questions": [
            "Describe the youth's friendships and social relationships.",
            "Does the youth have any prosocial friends or positive influences?",
            "Is there any gang involvement or association with delinquent peers?",
            "How does the youth spend free time with friends?"
        ]
    },
    "prior_offenses": {
        "priority": 1,
        "questions": [
            "Does the youth have any prior juvenile or criminal history?",
            "If yes, describe the nature and outcomes of prior offenses.",
            "Has the youth previously been on probation or in placement?"
        ]
    },
    "current_offense": {
        "priority": 1,
        "questions": [
            "What is the current offense that led to this referral?",
            "Describe the circumstances of the offense.",
            "What is the youth's attitude toward the offense?",
            "Were there any co-participants or victims?"
        ]
    },
    "strengths_protective_factors": {
        "priority": 3,
        "questions": [
            "What are the youth's strengths and positive qualities?",
            "Are there supportive adults in the youth's life (mentors, coaches, etc.)?",
            "What activities or interests is the youth passionate about?",
            "What goals does the youth have for the future?"
        ]
    }
}


def get_next_question(state: IntakeState) -> Optional[Dict[str, Any]]:
    """
    Determine the next question to ask based on coverage and priority.

    Args:
        state: Current intake state

    Returns:
        Dictionary with topic and question, or None if all topics covered
    """
    uncovered = state.get("uncovered_topics", [])

    if not uncovered:
        return None

    # Sort uncovered topics by priority
    topics_with_priority = [
        (topic, TOPIC_QUESTIONS.get(topic, {}).get("priority", 99))
        for topic in uncovered
        if topic in TOPIC_QUESTIONS
    ]
    topics_with_priority.sort(key=lambda x: x[1])

    if not topics_with_priority:
        return None

    # Get highest priority topic
    next_topic = topics_with_priority[0][0]
    topic_data = TOPIC_QUESTIONS[next_topic]

    # Get first question for this topic
    questions = topic_data.get("questions", [])
    if questions:
        return {
            "topic": next_topic,
            "question": questions[0],
            "all_questions": questions
        }

    return None


def generate_followup_question(
    topic: str,
    previous_answer: str,
    covered_questions: List[str]
) -> Optional[str]:
    """
    Generate a follow-up question based on the previous answer.

    This is a placeholder for LLM-based question generation.

    Args:
        topic: Current topic being discussed
        previous_answer: The previous answer from the youth/family
        covered_questions: Questions already asked for this topic

    Returns:
        Follow-up question or None if topic is complete
    """
    topic_data = TOPIC_QUESTIONS.get(topic, {})
    all_questions = topic_data.get("questions", [])

    # Find questions not yet asked
    remaining = [q for q in all_questions if q not in covered_questions]

    if remaining:
        return remaining[0]

    return None


def questioning_node(state: IntakeState) -> IntakeState:
    """
    Structured Questioning Agent Node.

    This node:
    1. Generates contextual questions based on responses
    2. Tracks coverage of required topics
    3. Adapts questioning based on risk factors
    4. Stores Q&A pairs in state

    Args:
        state: Current intake state

    Returns:
        Updated state with questioning progress
    """
    # Update phase
    state["current_phase"] = IntakePhase.QUESTIONING.value

    # Get next question to ask
    next_q = get_next_question(state)

    if next_q:
        # Add question to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"[Topic: {next_q['topic']}] {next_q['question']}"
        })
    else:
        # All topics covered, move to next phase
        state["messages"].append({
            "role": "system",
            "content": "All required topics have been covered. Moving to policy retrieval."
        })
        state["current_phase"] = IntakePhase.POLICY_RETRIEVAL.value

    return state


def record_response(
    state: IntakeState,
    topic: str,
    question: str,
    answer: str
) -> IntakeState:
    """
    Record a question-answer response in the state.

    Args:
        state: Current intake state
        topic: Topic of the question
        question: The question asked
        answer: The response received

    Returns:
        Updated state with recorded response
    """
    # Create Q&A record
    qa_record: QuestionAnswer = {
        "question": question,
        "answer": answer,
        "topic": topic,
        "timestamp": datetime.now().isoformat()
    }

    # Add to responses
    state["responses"].append(qa_record)

    # Update topic coverage
    if topic not in state["covered_topics"]:
        state["covered_topics"].append(topic)

    if topic in state["uncovered_topics"]:
        state["uncovered_topics"].remove(topic)

    return state


def check_for_risk_indicators(responses: List[QuestionAnswer]) -> List[Dict[str, Any]]:
    """
    Analyze responses for risk indicators that need follow-up.

    Args:
        responses: List of question-answer pairs

    Returns:
        List of identified risk indicators
    """
    risk_indicators = []

    # Keywords that indicate higher risk
    risk_keywords = {
        "high": [
            "suicide", "self-harm", "abuse", "violence", "gang",
            "weapon", "drugs", "arrested", "detention"
        ],
        "moderate": [
            "truancy", "suspended", "expelled", "fighting",
            "alcohol", "marijuana", "stealing"
        ]
    }

    for qa in responses:
        answer_lower = qa["answer"].lower()

        for level, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in answer_lower:
                    risk_indicators.append({
                        "level": level,
                        "keyword": keyword,
                        "topic": qa["topic"],
                        "context": qa["answer"][:100]
                    })

    return risk_indicators
