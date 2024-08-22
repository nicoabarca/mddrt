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
        from IPython.display import Image, display

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)
        display(Image(graph_path))
    else:
        from PIL import Image, UnidentifiedImageError

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)
        try:
            img = Image.open(graph_path)
            img.show()
        except UnidentifiedImageError as e:
            print(f"ERROR: {e}. Enter a valid image file format like png, jpg, jpeg, etc.")
        finally:
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
