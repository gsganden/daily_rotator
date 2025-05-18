import modal

from main import app as fasthtml_app

app = modal.App(
    name="daily-rotator",
    image=modal.Image.debian_slim()
    .pip_install_from_pyproject("pyproject.toml")
    .add_local_file("main.py", "/root/main.py"),  # Copy main.py to the image
)


@app.function()
@modal.asgi_app()
def web_app():
    return fasthtml_app
