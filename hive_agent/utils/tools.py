from typing import List, Callable

from llama_index.core.tools import FunctionTool


# TODO: receive name and description individually
def tools_from_funcs(funcs: List[Callable], name="", description="") -> List[FunctionTool]:
    return [FunctionTool.from_defaults(fn=func, name=name, description=description) for func in funcs] if funcs else []
