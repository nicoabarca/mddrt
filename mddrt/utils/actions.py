import os
import platform
import subprocess
import tempfile

from graphviz import Source


def save_graphviz_diagram(drt_string: str, filename: str, format: str):
    graph = Source(drt_string)
    graph.render(filename=filename, format=format, cleanup=True)


def view_graphviz_diagram(drt_string: str, format: str):
    filename = "tmp_source_file"
    file_format = format
    graph = Source(drt_string)

    if is_google_colab() or is_jupyter_notebook():
        if format not in ["jpg", "png", "jpeg", "svg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png', 'jpeq' or 'svg'"
            raise ValueError(msg_error)
        from IPython.display import SVG, Image, display

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)

        if format == "svg":
            display(SVG(filename=graph_path))
        else:
            display(Image(graph_path))
    else:
        from PIL import Image

        if format not in ["jpg", "png", "jpeg", "webp", "svg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png', 'jpeq', 'webp' or 'svg'"
            raise ValueError(msg_error)

        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file_path = temp_file.name
        graph_path = graph.render(filename=temp_file_path, format=file_format, cleanup=True)

        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", f"{temp_file_path}.{format}"))
        elif platform.system() == "Windows":  # Windows
            os.startfile(f"{temp_file_path}.{format}")
        else:  # linux variants
            subprocess.call(("xdg-open", f"{temp_file_path}.{format}"))


def is_jupyter_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" in get_ipython().config:
            return True
    except (ImportError, AttributeError, KeyError):
        return False


def is_google_colab():
    try:
        import google.colab

        return False
    except ImportError:
        return False
