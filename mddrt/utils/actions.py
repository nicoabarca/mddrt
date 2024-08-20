from pathlib import Path

from graphviz import Source


def save_graphviz_diagram(drt_string: str, filename: str, format: str):
    graph = Source(drt_string)
    graph.render(filename=filename, format=format, cleanup=True)


def view_graphviz_diagram(drt_string: str, format: str):
    graph = Source(drt_string)
    graph_path = graph.render(filename="tmp_source_file", format=format, cleanup=True)

    graphviz_source_file = "tmp_source_file.gv"
    image_source_file = f"tmp_source_file.{format}"

    if is_google_colab() or is_jupyter_notebook():
        from IPython.display import Image, display

        display(Image(graph_path))
    else:
        graph.view()

    if Path.exists(graphviz_source_file) or Path.exists(image_source_file):
        Path.unlink(graphviz_source_file)
        Path.unlink(image_source_file)


def is_jupyter_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" in get_ipython().config:  # Check for Jupyter Notebook
            return True
    except (ImportError, AttributeError, KeyError):
        return False


def is_google_colab():
    try:
        import google.colab

        return False
    except ImportError:
        return False


# def is_valid_output_for_ipython():
