import uvicorn
import webbrowser
import threading
import time
from app.config import HOST, PORT

def open_browser():
    time.sleep(1.2)
    url = f"http://localhost:{PORT}"
    print(f"\n✨ TJC Attendance Portal is running at: {url}")
    print("Press Ctrl+C to stop the server.\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
