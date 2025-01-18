import mistune
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def markdown_to_html_email(markdown_filepath, recipient_email, sender_email, sender_password, subject="Markdown to HTML Email", attachments=None):
    """
    Converts a Markdown file to HTML using mistune, then sends it as an email with optional attachments.

    Args:
        markdown_filepath: Path to the Markdown file.
        recipient_email: Email address of the recipient.
        sender_email: Email address of the sender.
        sender_password: Password for the sender's email account (use app passwords or environment variables).
        subject: Subject of the email.
        attachments: List of file paths to attach to the email (default: None).
    """
    try:
        # Read the Markdown file
        with open(markdown_filepath, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        # Convert Markdown to HTML
        renderer = mistune.HTMLRenderer()  # Initialize the renderer
        markdown = mistune.Markdown(renderer=renderer)  # Initialize the markdown parser with the renderer
        html_content = markdown(markdown_text)  # Process the markdown

        # Create the email message
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email

        # Attach plain text and HTML versions of the email
        part1 = MIMEText(markdown_text, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)

        # Attach files if provided
        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)  # Encode the attachment in base64
                    filename = os.path.basename(filepath)  # Extract the filename
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    message.attach(part)
                    print(f"Attached: {filename}")
                except FileNotFoundError:
                    print(f"Error: Attachment not found: {filepath}")
                except Exception as e:
                    print(f"Error attaching {filepath}: {e}")

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        print(f"Email sent successfully to {recipient_email}")

    except FileNotFoundError:
        print(f"Error: File not found: {markdown_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# if __name__ == "__main__":
#     markdown_file = r"C:\Users\USER\Downloads\gen-ai\Forex-Analysis.md"
#     recipient = "recipient@example.com"
#     sender = "sender@gmail.com"
#     password = "your_app_password"  # Use an app-specific password for Gmail
#     subject_line = "Daily Forex Analysis"
#     attachments = [
#         r"C:\Users\USER\Downloads\gen-ai\attachment1.pdf",
#         r"C:\Users\USER\Downloads\gen-ai\image.png"
#     ]

#     markdown_to_html_email(markdown_file, recipient, sender, password, subject_line, attachments)