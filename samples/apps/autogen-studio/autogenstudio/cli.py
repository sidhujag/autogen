import os
from typing_extensions import Annotated
import typer
import uvicorn
from multiprocessing import Process

# Assuming .version and .utils.dbutils are modules in your package
from .version import VERSION
from .utils.dbutils import DBManager

app = typer.Typer()

def run_server(host, port, reload, workers):
    uvicorn.run(
        "autogenstudio.web.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
    )

@app.command()
def ui(
    host: str = "127.0.0.1",
    port: int = 8081,
    workers: int = 1,
    reload: Annotated[bool, typer.Option("--reload")] = False,
    docs: bool = False,
    appdir: str = None,
):
    """
    Run the AutoGen Studio UI.

    Args:
        host (str, optional): Host to run the UI on. Defaults to 127.0.0.1 (localhost).
        port (int, optional): Port to run the UI on. Defaults to 8081.
        workers (int, optional): Number of workers to run the UI with. Defaults to 1.
        reload (bool, optional): Whether to reload the UI on code changes. Defaults to False.
        docs (bool, optional): Whether to generate API docs. Defaults to False.
        appdir (str, optional): Path to the AutoGen Studio app directory. Defaults to None.
    """
    os.environ["AUTOGENSTUDIO_API_DOCS"] = str(docs)
    if appdir:
        os.environ["AUTOGENSTUDIO_APPDIR"] = appdir

    # Start the first server in a separate process
    process1 = Process(target=run_server, args=(host, port - 1, reload, workers))
    process1.start()
    
    try:
        # Start the second server in the main thread
        uvicorn.run(
            "autogenstudio.web.app:app",
            host=host,
            port=port,
            workers=workers,
            reload=reload,
        )
    except KeyboardInterrupt:
        # This block may not be necessary since uvicorn handles CTRL+C gracefully
        pass
    finally:
        # Ensure the subprocess is terminated when exiting the main server
        process1.terminate()
        process1.join()

@app.command()
def version():
    """
    Print the version of the SuperDapp Studio UI CLI.
    """
    typer.echo(f"SuperDapp Studio CLI version: {VERSION}")

def run():
    app()

if __name__ == "__main__":
    run()
