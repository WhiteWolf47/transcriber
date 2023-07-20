from cx_Freeze import setup, Executable

setup(
    name="trsapp",
    version="1.0",
    description="Description of your app",
    executables=[Executable("main.py")]
)
