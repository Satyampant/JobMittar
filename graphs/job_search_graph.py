
from langgraph.graph import StateGraph, END
from graphs.state import JobMittrState, create_initial_state


def create_job_mittr_graph() -> StateGraph:
    graph = StateGraph(JobMittrState)
    return graph


def compile_graph() -> any:
    graph = create_job_mittr_graph()
    return graph.compile()

