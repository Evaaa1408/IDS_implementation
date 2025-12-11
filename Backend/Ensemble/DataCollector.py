#DataCollector.py
import os
import pandas as pd
import datetime
import uuid

class DataCollector:
    def __init__(self, base_dir=None):
        if base_dir:
            self.base_dir = base_dir
        else:
            # Default to FYP_Implementation/Dataset
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Dataset'))
        
        self.log_file = os.path.join(self.base_dir, "self_learning_data.csv")
        self.malicious_log_file = os.path.join(self.base_dir, "malicious_log.txt") 
        self.html_storage_dir = os.path.join(self.base_dir, "html_logs")
        
        # Ensure directories exist
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.html_storage_dir, exist_ok=True)
        
        # Initialize CSV if not exists
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=[
                "id", "timestamp", "url", "prob_2023", "prob_2025", 
                "final_prob", "is_phishing", "html_path"
            ])
            df.to_csv(self.log_file, index=False)
            print(f"🆕 Created new self-learning log: {self.log_file}")
        else:
            print(f"✅ Found existing self-learning log: {self.log_file}")

    def log_result(self, url, result_dict, html_content=None):
        """
        Logs a prediction result for future training.
        Saves HTML content to a separate file if provided.
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_path = ""
        if html_content:
            try:
                # Save HTML to a file to avoid massive CSVs
                filename = f"{request_id}.html"
                file_path = os.path.join(self.html_storage_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                html_path = filename
            except Exception as e:
                print(f"⚠️ Failed to save HTML snapshot: {e}")

        # Prepare row
        new_row = {
            "id": request_id,
            "timestamp": timestamp,
            "url": url,
            "prob_2023": result_dict.get("prob_2023", -1),
            "prob_2025": result_dict.get("prob_2025", -1),
            "final_prob": result_dict.get("final_probability", -1),
            "is_phishing": result_dict.get("is_phishing", False),
            "html_path": html_path
        }
        
        # -----------------------------------------------
        # Feature: Malicious Log (User Request)
        # -----------------------------------------------
        if new_row["is_phishing"]:
            try:
                log_entry = f"[{timestamp}] MALICIOUS DETECTED | URL: {url} | Confidence: {new_row['final_prob']:.4f}\n"
                with open(self.malicious_log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                print(f"🚨 Logged to malicious_log.txt: {url}")
            except Exception as e:
                print(f"⚠️ Failed to write to malicious_log.txt: {e}")

        try:
            # Append to CSV
            df = pd.DataFrame([new_row])
            df.to_csv(self.log_file, mode='a', header=False, index=False)
            print(f"📝 Logged request {request_id} for self-learning.")
            return request_id
        except Exception as e:
            print(f"❌ Failed to log to CSV: {e}")
            return None
