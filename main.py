from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from threading import Thread
from dotenv import load_dotenv
import os
import time

def send_mail(email):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    receiver_address = email
    sender_address = "jgabbayj@gmail.com"
    sender_pass = 'ovzzrduhoplxkjpn'
    message = MIMEMultipart('alternative')
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'מקום פנוי'  # The subject line
    text = "התפנה מקום, יש לך 20 דקות להזמין אותו, בהצלחה"
    # The body and the attachments for the mail
    message.attach(MIMEText(text, "plain"))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    session.sendmail(sender_address, receiver_address, message.as_string())
    session.quit()
    print('Mail Sent')


def main(url: str, username, password, email):
    USERNAME = username
    PASSWORD = password
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    LEFT_ZONES = list(range(0,9))+list(range(32,44))
    
    while True:
        username_element = WebDriverWait(driver, 864000).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_element = driver.find_element(By.ID, "password")
        driver.implicitly_wait(1)
        username_element.send_keys(USERNAME)
        password_element.send_keys(PASSWORD)
        login_button_element = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "btnLogin"))
        )
        login_button_element.click()
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "ctl00_spw1153_ctl00_steps_ctl00_stepContent"))
            )
            break
        except:
            driver.refresh()
    had_green_or_yellow_seats = True
    while True:
        available_zones = []
        if had_green_or_yellow_seats:
            green_available_zones = driver.find_elements(By.CLASS_NAME, "avail-green")
            yellow_available_zones = driver.find_elements(By.CLASS_NAME, "avail-yellow")
            if green_available_zones or yellow_available_zones:
                available_zones.extend(green_available_zones)
                available_zones.extend(yellow_available_zones)
            else:
                had_green_or_yellow_seats = False
        available_zones.extend(driver.find_elements(By.CLASS_NAME, "avail-red"))
        print("available zones=" + str(len(available_zones)))
        if available_zones:
            available_zones = [x for x in available_zones if
                               int(x.get_attribute("data-areaindex")) < 72]
            print("available_zones after filter=" + str(len(available_zones)))
            if not available_zones:
                driver.refresh()
                continue
            close_annoying_windows(driver)
            chosen_zone = available_zones[0]
            chosen_zone.click()
            if int(chosen_zone.get_attribute("data-areaindex")) not in LEFT_ZONES:
                print("case 1")
                seats_parents_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "zoomContainer"))
                )
                seats_elements = seats_parents_element.find_elements(By.TAG_NAME, "img")
                available_seats_elements = [x for x in seats_elements if x.get_attribute("data-firstfreeseatinrow")]
                good_seats_elements = [x for x in available_seats_elements if
                                       7 < int(x.get_attribute("alt").split("/")[0]) < 32]
                best_seats_elements = [x for x in available_seats_elements if
                                       12 < int(x.get_attribute("alt").split("/")[0]) < 18 or 26 < int(
                                           x.get_attribute("alt").split("/")[0]) < 30]
                print("available seats=" + str(len(available_seats_elements)) + " good seats=" + str(
                    len(good_seats_elements)) + " best seats=" + str(len(best_seats_elements)))
                available_seats_elements = best_seats_elements + good_seats_elements + available_seats_elements
                if not available_seats_elements:
                    driver.back()
                    continue
                close_annoying_windows(driver)
                available_seats_elements[0].click()
                send_mail(email)
                break
            else:
                print("case 2")
                WebDriverWait(driver, 10).until(
                    EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, ".count.numericSpinner.ui-spinner-input"), "0")
                )
                input_spinner = driver.find_element(By.CSS_SELECTOR, ".count.numericSpinner.ui-spinner-input")
                input_spinner.clear()
                input_spinner.send_keys("1")
                button_proceed = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "btnProceed"))
                )
                button_proceed.click()
                send_mail(email)
                break


def close_annoying_windows(driver):
    classes = [".ui-button.ui-corner-all.ui-widget.ui-button-icon-only.ui-dialog-titlebar-close", ".ui-button.showPopupMessage-bluebutton.ui-corner-all.ui-widget"]
    for cls in classes:
        try:
            annoying_window = driver.find_element(By.CSS_SELECTOR,
                                                  cls)
            annoying_window.click()
        except Exception as e:
            pass


if __name__ == "__main__":
    load_dotenv()
    username = os.environ.get("USER")
    password = os.environ.get("PASSWORD")
    email = os.environ.get("EMAIL")
    if not username or not password or not email:
        if not username or not password:
            print("Enter username and password:")
            username = input("username: ")
            password = input("password: ")
        if not email:
            email = input("Enter email address of recipient: ")
        open(".env","w").write(f"USER={username}\nPASSWORD={password}\nEMAIL={email}")        
    num_threads = int(input("Number of tickets: "))
    url = input("Enter event url: ")
    threads = []
    for i in range(num_threads):
        threads.append(Thread(target=main, args=[url, username, password, email]))
    for t in threads:
        t.start()
    for t in threads:
        t.join()



