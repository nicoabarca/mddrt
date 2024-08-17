import shutil
import tempfile

from graphviz import Source


def save_graphviz_diagram(dfg_string: str, file_path: str, format: str):
    tmp_file = tempfile.NamedTemporaryFile(suffix=".gv")
    tmp_file.close()
    src = Source(dfg_string, tmp_file.name, format=format)

    render = src.render(cleanup=True)
    shutil.copyfile(render, f"{file_path}.{format}")
