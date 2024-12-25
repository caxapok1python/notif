def send_sms(to_phone: str, text: str):
    """
    Заглушка отправки SMS.
    В реальном проекте можно интегрировать:
    - Twilio
    - SMSC
    - etc
    """
    print(f"[SMS] Отправлено на {to_phone}: {text}")