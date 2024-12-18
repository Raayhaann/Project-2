import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)  
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Database connection
DB_PATH = os.path.join(os.path.dirname(__file__), "Database", "reports.db")

CSV_FILE_PATH = os.path.join(os.getcwd(), "reports.csv")

def load_data():
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        return df
    except Exception as e:
        return f"مشكلة مع ملف CSV: {e}"  # Return error message if any issue occurs

def load_pdf(file_id):
    """
    Loads the PDF file path from the CSV file based on the file ID.
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        file_path = df.loc[df['id'] == file_id, 'pdf_path'].squeeze()
        if not pd.isna(file_path):
            return file_path
        return None
    except Exception as e:
        return f"مشكلة مع ملف CSV: {e}"

def load_md(file_id):
    """
    Loads the MD file path from the CSV file based on the file ID.
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        row = df[df['id'] == file_id]
        
        if not row.empty:
            
            file_path = row.iloc[0]['md_path']
            return file_path
        return None
    except Exception as e:
        return f"مشكلة مع ملف CSV: {e}", None

    
# def load_data():  # Ensure this function is correctly defined in your file
#     conn = sqlite3.connect(DB_PATH)
#     try:
#         query = "SELECT id, report_type, year, name FROM reports"
#         df = pd.read_sql_query(query, conn)
#         return df
#     except pd.io.sql.DatabaseError as e:
#         return f"مشكلة مع قاعدة البيانات: {e}"  # Return error message if any issue occurs
#     finally:
#         conn.close()


# def load_pdf(file_id):
#     """
#     Loads the PDF file from the database based on the file ID.
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT name, pdf_file FROM reports WHERE id = ?", (file_id,))
#         row = cursor.fetchone()
#         if row:
#             return row[0], row[1]  # Returning the name and the pdf_file content
#         return None, None
#     except sqlite3.Error as e:
#         return f"Database error: {e}", None
#     finally:
#         conn.close()


# def load_md(file_id):
#     """
#     Loads the MD file from the database based on the file ID.
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT name, md_file FROM reports WHERE id = ?", (file_id,))
#         row = cursor.fetchone()
#         if row:
#             return row[0], row[1]  # Returning the name and the md_file content
#         return None, None
#     except sqlite3.Error as e:
#         return f"Database error: {e}", None
#     finally:
#         conn.close()



def summarize_text(text):
    try:
        url = "http://127.0.0.1:1234/v1/chat/completions"
        payload = {
            "model": "meta-llama-3.1-8b-instruct",
            "messages": [
              {"role": "system", "content": "Always summarize in good markdown clean organized format and use bullet points."},
                {"role": "user", "content": f'قم بتخليص الملف التالي باللغة العربية: {text}'}
            ],
            "temperature": 0,
            "max_tokens": 512,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error communicating with LLM server: {e}"
    except (KeyError, IndexError) as e:
        return f"خلل في معالجة الرد: {e}"
    except Exception as e:
        return f"حدث خطأ غير متوقع: {e}"


def summarize_text_gemini(text):
    try:
        response = gemini_model.generate_content(f"قم بتلخيص النص التالي باللغة العربية مع استخدام نقاط وعناوين منظمة و شاملة {text}")
        return response.text
    except Exception as e:
        return f"يوجد خلل في التلخيص : {e}"
    
def summarize_text_gemini_stream(text):
    try:
        response = gemini_model.generate_content(f"قم بتلخيص النص التالي باللغة العربية مع استخدام نقاط وعناوين منظمة و شاملة {text}",stream=True)
        for chunk in response:
            yield chunk.get("text","")
    except Exception as e:
        return f"يوجد خلل في التلخيص : {e}"
