import traceback
from datetime import datetime

def log_error(e: Exception):
    # Error ki poori detail nikalna
    error_details = traceback.format_exc()
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # File mein save karna
    with open("server_error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n\n--- ERROR AT {time_now} ---\n")
        f.write(f"TYPE: {type(e).__name__}\n")
        f.write(f"MESSAGE: {str(e)}\n")
        f.write(f"TRACEBACK:\n{error_details}\n")
        f.write("="*50)