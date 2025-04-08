import time
import smtplib
from email.mime.text import MIMEText
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# --- CONFIG ---
USERNAME = "rohan.singhal@gmail.com"
PASSWORD = "password1234"
LOGIN_URL = "https://prenotami.esteri.it/Services/Booking/5194"
NO_APPOINTMENT_TEXT = "Stante l'elevata richiesta i posti disponibili per il servizio scelto sono esauriti."

# Email settings
SEND_FROM = "your_gmail@gmail.com"
SEND_TO = "your_email@example.com"
APP_PASSWORD = "your_app_password"

# --- FUNCTION TO CHECK APPOINTMENT ---
def check_appointment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(LOGIN_URL)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-email"))).send_keys(USERNAME)
        driver.find_element(By.ID, "login-password").send_keys(PASSWORD)
        driver.find_element(By.ID, "login-button").click()

        avanti_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Avanti")]'))
        )
        avanti_button.click()

        time.sleep(5)
        page_text = driver.page_source

        if NO_APPOINTMENT_TEXT not in page_text:
            msg = MIMEText("An appointment may be available at prenotami. Check it ASAP!")
            msg["Subject"] = "[ALERT] Prenotami Appointment Available"
            msg["From"] = SEND_FROM
            msg["To"] = SEND_TO

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SEND_FROM, APP_PASSWORD)
                server.send_message(msg)

            return {"status": "alert_sent", "message": "Appointment may be available."}
        else:
            return {"status": "no_appointment", "message": "No appointment available."}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        driver.quit()

# --- FLASK ROUTE ---
@app.route("/check", methods=["GET"])
def trigger_check():
    result = check_appointment()
    return jsonify(result)

# --- RUN FLASK APP ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
