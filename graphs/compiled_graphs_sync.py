
from graphs.master_graph import build_master_graph
from graphs.checkpointers import get_checkpointer


def compile_master_graph_sync():
    checkpointer = get_checkpointer()
    
    graph = build_master_graph()
    compiled = graph.compile(checkpointer=checkpointer)
    
    return compiled
