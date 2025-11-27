"""Resume processing subgraph: parse → analyze → validate → END."""

from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState
from graphs.nodes.resume_nodes import (
    parse_resume_node,
    analyze_resume_node,
    validate_resume_node
)


def create_resume_subgraph() -> StateGraph:
    """Create resume processing subgraph with sequential nodes.
    
    Flow:
    1. parse_resume_node: Extract structured data from raw text
    2. analyze_resume_node: Generate AI quality analysis
    3. validate_resume_node: Check required fields
    4. END
    
    Returns:
        Compiled StateGraph for resume processing
    """
    # Initialize subgraph with state schema
    subgraph = StateGraph(JobMittrState)
    
    # Add nodes in processing order
    subgraph.add_node("parse_resume", parse_resume_node)
    subgraph.add_node("analyze_resume", analyze_resume_node)
    subgraph.add_node("validate_resume", validate_resume_node)
    
    # Set entry point
    subgraph.set_entry_point("parse_resume")
    
    # Wire sequential flow
    subgraph.add_edge("parse_resume", "analyze_resume")
    subgraph.add_edge("analyze_resume", "validate_resume")
    subgraph.add_edge("validate_resume", END)
    
    return subgraph


def compile_resume_subgraph():
    """Compile resume subgraph into executable workflow.
    
    Returns:
        Compiled graph ready for invocation
    """
    subgraph = create_resume_subgraph()
    return subgraph.compile()


# Example usage and testing
if __name__ == "__main__":
    print("Testing Resume Processing Subgraph")
    print("=" * 60)
    
    # Create compiled graph
    graph = compile_resume_subgraph()
    
    # Test Case 1: Valid resume
    print("\n[Test 1] Valid Resume Processing")
    print("-" * 60)
    
    test_state = {
        "resume_data": {
            "raw_text": """
            John Doe
            john.doe@example.com | (555) 123-4567
            
            SUMMARY
            Experienced software engineer with 5 years in full-stack development.
            
            SKILLS
            Python, JavaScript, React, Node.js, SQL, Docker, AWS
            
            EXPERIENCE
            Senior Software Engineer | Tech Corp | 2021-Present
            - Led development of microservices architecture
            - Improved system performance by 40%
            
            EDUCATION
            BS Computer Science | MIT | 2019
            """
        },
        "current_step": "resume_upload",
        "job_results": [],
        "messages": []
    }
    
    result = graph.invoke(test_state)
    
    print(f"✓ Final step: {result.get('current_step')}")
    print(f"✓ Name extracted: {result.get('resume_data', {}).get('name')}")
    print(f"✓ Email extracted: {result.get('resume_data', {}).get('email')}")
    print(f"✓ Skills count: {len(result.get('resume_data', {}).get('skills', []))}")
    print(f"✓ Analysis available: {'analysis' in result.get('resume_data', {})}")
    print(f"✓ Error: {result.get('error', 'None')}")
    
    if result.get('resume_data', {}).get('analysis'):
        analysis = result['resume_data']['analysis']
        print(f"✓ Strengths: {len(analysis.get('strengths', []))}")
        print(f"✓ Weaknesses: {len(analysis.get('weaknesses', []))}")
    
    # Test Case 2: Invalid resume (missing required fields)
    print("\n[Test 2] Invalid Resume - Validation Failure")
    print("-" * 60)
    
    invalid_state = {
        "resume_data": {
            "raw_text": "This is not a proper resume."
        },
        "current_step": "resume_upload",
        "job_results": [],
        "messages": []
    }
    
    result_invalid = graph.invoke(invalid_state)
    
    print(f"✓ Final step: {result_invalid.get('current_step')}")
    print(f"✓ Error detected: {result_invalid.get('error', 'None')}")
    
    # Test Case 3: Empty resume
    print("\n[Test 3] Empty Resume Text")
    print("-" * 60)
    
    empty_state = {
        "resume_data": {
            "raw_text": ""
        },
        "current_step": "resume_upload",
        "job_results": [],
        "messages": []
    }
    
    result_empty = graph.invoke(empty_state)
    
    print(f"✓ Final step: {result_empty.get('current_step')}")
    print(f"✓ Error detected: {result_empty.get('error', 'None')}")
    
    print("\n" + "=" * 60)
    print("Resume Subgraph Tests Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("- Integrate subgraph into main workflow")
    print("- Add conditional routing based on validation")
    print("- Connect to job search nodes")