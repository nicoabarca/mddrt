import os

from graphviz import Source


def save_graphviz_diagram(drt_string: str, filename: str, format: str):
    graph = Source(drt_string)
    graph.render(filename=filename, format=format, cleanup=True)


def view_graphviz_diagram(drt_string: str, format: str):
    filename = "tmp_source_file"
    file_format = format
    graph = Source(drt_string)

    if is_google_colab() or is_jupyter_notebook():
        if format not in ["jpg", "png", "jpeg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png' or 'jpeq'"
            raise ValueError(msg_error)
        from IPython.display import Image, display

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)
        display(Image(graph_path))
    else:
        from PIL import Image

        if format not in ["jpg", "png", "jpeg", "webp", "svg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png', 'jpeq', 'webp' or 'svg'"
            raise ValueError(msg_error)

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)
        img = Image.open(graph_path)
        img.show()
        os.remove(graph_path)


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
