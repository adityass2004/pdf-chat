import subprocess
import sys
import os

def run_streamlit():
    """Run the Streamlit app"""
    # Get the directory where main.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    streamlit_app = os.path.join(current_dir, "src", "app.py")
    
    # Check if app.py exists
    if not os.path.exists(streamlit_app):
        print(f"Error: {streamlit_app} not found!")
        print("Please make sure app.py is in the src directory")
        sys.exit(1)
    
    # Run Streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        streamlit_app,
        "--server.port=8501",
        "--server.headless=true"
    ])

if __name__ == "__main__":
    print("Starting PDF Chat Streamlit Application...")
    print("=" * 70)
    print("The app will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)