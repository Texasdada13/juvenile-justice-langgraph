"""
Intake Triage Assistant - Main Entry Point

A LangGraph-powered multi-agent system for juvenile justice intake processing.
"""

import os
import sys
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import create_initial_state, IntakeState
from src.graph import compile_graph, get_graph_diagram
from src.nodes.questioning import record_response
from src.nodes.human_review import process_approval, get_review_prompt, create_audit_record


def run_demo():
    """
    Run a demonstration of the Intake Triage Assistant.

    This simulates an intake process with sample data.
    """
    print("=" * 60)
    print("INTAKE TRIAGE ASSISTANT - DEMO")
    print("=" * 60)
    print()

    # Show the workflow diagram
    print("WORKFLOW DIAGRAM:")
    print(get_graph_diagram())
    print()

    # Create initial state with sample youth data
    print("Initializing case with sample data...")
    initial_state = create_initial_state(
        intake_officer="Officer Smith",
        youth_info={
            "name": "John Doe",
            "date_of_birth": "2009-05-15",
            "gender": "Male",
            "race": "White"
        },
        guardian_info={
            "name": "Jane Doe",
            "relationship": "Mother",
            "phone": "(555) 123-4567"
        },
        referral_info={
            "source": "School Resource Officer",
            "reason": "Theft - Shoplifting",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    )

    print(f"Case ID: {initial_state['case_id']}")
    print(f"Youth: {initial_state['youth_info']['name']}")
    print(f"Referral: {initial_state['referral_info']['reason']}")
    print()

    # Add sample interview responses
    print("Adding sample interview responses...")

    sample_responses = [
        ("family_situation", "Who does the youth live with?",
         "Lives with mother and younger sister. Parents divorced 2 years ago. Father has limited contact. Mother works two jobs and has difficulty supervising."),

        ("education", "How is the youth doing in school?",
         "Currently enrolled in 9th grade. Has been truant several times this semester. Grades have dropped from Bs to Ds. No IEP."),

        ("peer_relations", "Describe the youth's friendships.",
         "Has a small group of friends from school. One friend has been in trouble with the law. Also has some prosocial friends from basketball team."),

        ("substance_use", "Has the youth ever used substances?",
         "Admits to trying marijuana once at a party. Denies regular use. No alcohol use reported."),

        ("mental_health", "Any mental health concerns?",
         "No formal diagnosis. Mother reports youth has been more withdrawn since divorce. Some anger management issues noted at school."),

        ("prior_offenses", "Any prior legal history?",
         "No prior arrests or referrals. This is first contact with juvenile justice system."),

        ("current_offense", "Describe the current offense.",
         "Youth was caught shoplifting $50 worth of items from a store. Youth admits to the offense and expressed regret. No co-participants."),

        ("strengths_protective_factors", "What are the youth's strengths?",
         "Good at basketball, on the school team. Has goals of going to college. Mother is supportive despite work schedule. Has an uncle who is a positive mentor.")
    ]

    for topic, question, answer in sample_responses:
        initial_state = record_response(initial_state, topic, question, answer)

    print(f"Added {len(sample_responses)} interview responses.")
    print()

    # Compile and run the graph
    print("Compiling LangGraph workflow...")

    try:
        graph = compile_graph()
        print("Graph compiled successfully!")
        print()

        # Run the workflow
        print("Running intake workflow...")
        print("-" * 40)

        # Since we've pre-populated responses, adjust the state
        initial_state["uncovered_topics"] = []  # All topics covered

        # Run the graph
        result = graph.invoke(initial_state)

        print()
        print("=" * 60)
        print("WORKFLOW COMPLETE")
        print("=" * 60)
        print()

        # Display the case summary
        print("GENERATED CASE SUMMARY:")
        print()
        print(result.get("case_summary", "No summary generated"))
        print()

        # Display recommendations
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(result.get("recommendations", []), 1):
            print(f"  {i}. {rec}")
        print()

        # Show eligibility results
        print("ELIGIBILITY SUMMARY:")
        for er in result.get("eligibility_results", []):
            status = er.get("status", "unknown").upper()
            name = er.get("program_name", "Unknown")
            print(f"  [{status}] {name}")
        print()

        # Show risk level
        print(f"RISK LEVEL: {result.get('risk_level', 'unknown').upper()}")
        print()

        # Create audit record
        audit = create_audit_record(result)
        print("AUDIT RECORD CREATED")
        print(f"  Questions asked: {audit['questions_asked']}")
        print(f"  Topics covered: {len(audit['topics_covered'])}")
        print()

        return result

    except ImportError as e:
        print(f"Import error: {e}")
        print()
        print("Note: This demo requires LangGraph to be installed.")
        print("Install with: pip install langgraph")
        print()
        print("Running in simulation mode without LangGraph...")
        return run_simulation(initial_state)


def run_simulation(state: IntakeState) -> IntakeState:
    """
    Run a simulated workflow without LangGraph.

    Useful for testing when LangGraph is not installed.

    Args:
        state: Initial state

    Returns:
        Final state after simulation
    """
    from src.nodes.intake import intake_node
    from src.nodes.policy_retrieval import policy_retrieval_node
    from src.nodes.eligibility import eligibility_node
    from src.nodes.risk_assessment import risk_assessment_node
    from src.nodes.summary import summary_node
    from src.nodes.human_review import human_review_node

    print("Running nodes sequentially...")

    # Run each node
    state = intake_node(state)
    print("  [✓] Intake node complete")

    state = policy_retrieval_node(state)
    print("  [✓] Policy retrieval complete")

    state = eligibility_node(state)
    print("  [✓] Eligibility checking complete")

    state = risk_assessment_node(state)
    print("  [✓] Risk assessment complete")

    state = summary_node(state)
    print("  [✓] Summary generation complete")

    state = human_review_node(state)
    print("  [✓] Ready for human review")

    print()
    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print()

    # Display results
    print("GENERATED CASE SUMMARY:")
    print()
    print(state.get("case_summary", "No summary generated"))

    return state


def main():
    """Main entry point."""
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     JUVENILE JUSTICE INTAKE TRIAGE ASSISTANT            ║")
    print("║     POC #1 - LangGraph Multi-Agent System               ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    run_demo()


if __name__ == "__main__":
    main()
