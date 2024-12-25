def send_email(to_email: str, subject: str, body: str):
    """
    Заглушка отправки email.
    В реальном проекте можно интегрировать:
    - SMTP
    - SendGrid
    - Mailgun
    - и т.д.
    """
    print(f"[EMAIL] Отправлено на {to_email}: {subject}\n{body}")

