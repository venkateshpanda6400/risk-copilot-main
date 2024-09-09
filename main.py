import multiprocessing
import subprocess
import warnings
warnings.filterwarnings("ignore")


def run_script(script_name):
    subprocess.run(["python3", script_name])


def run_streamlit(script_name, port):
    subprocess.run(["streamlit", "run", script_name, "--server.port", str(port)])


if __name__ == "__main__":
    # Create two processes
    p1 = multiprocessing.Process(
        target=run_streamlit, args=("src/riskCopilot/admin.py", 8080)
    )
    p2 = multiprocessing.Process(
        target=run_script, args=("src/riskCopilot/monitor.py",)
    )

    p3 = multiprocessing.Process(
        target=run_streamlit, args=("src/riskCopilot/app.py", 8000)
    )

    # Start both processes
    p1.start()
    p2.start()
    p3.start()

    # Wait for both processes to finish
    p1.join()
    p2.join()
    p3.join()

    print("Both scripts have finished running.")
