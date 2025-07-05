import imaplib
import email
import smtplib
import time
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
import ssl
from datetime import datetime, timedelta
import re
import getpass

# === COLLECTE INTERACTIVE DES IDENTIFIANTS ===
print("=== Configuration de votre transfert de mails ===")
IMAP_HOST = input("Serveur IMAP (ex: imap.univ-rouen.fr) : ").strip()
IMAP_USER = input("Adresse mail source (IMAP) : ").strip()
IMAP_PASS = getpass.getpass("Mot de passe de cette adresse : ")

SMTP_HOST = input("Serveur SMTP (ex: smtp.gmail.com) : ").strip()
SMTP_PORT = int(input("Port SMTP (ex: 587) : ").strip())
SMTP_USER = input("Adresse mail destination (SMTP) : ").strip()
SMTP_PASS = getpass.getpass("Mot de passe (ou mot de passe d'application) : ")

# === UTILITAIRE POUR NETTOYER LES EN-TÊTES ===
def nettoyer_header(texte):
    if texte:
        return re.sub(r'[\r\n]+', ' ', texte).strip()
    return ''

# === BOUCLE PRINCIPALE ===
while True:
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST)
        imap.login(IMAP_USER, IMAP_PASS)
        imap.select('INBOX')

        date_limite = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
        search_criteria = f'(UNSEEN SINCE {date_limite})'
        status, messages = imap.search(None, search_criteria)
        transferred = []

        for num in messages[0].split():
            print(f"📨 Traitement du mail UID {num.decode()}")
            status, data = imap.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            original = email.message_from_bytes(raw_email)

            msg = EmailMessage()
            subject = original.get('Subject')
            msg['Subject'] = nettoyer_header(subject) if subject else '(Sans objet)'
            msg['From'] = nettoyer_header(original.get('From'))
            msg['To'] = SMTP_USER
            msg['Reply-To'] = nettoyer_header(original.get('Reply-To') or original.get('From'))
            msg['Date'] = nettoyer_header(original.get('Date', formatdate()))
            msg['Message-ID'] = make_msgid()
            msg['X-Original-From'] = nettoyer_header(original.get('From'))
            msg['X-Original-To'] = nettoyer_header(original.get('To'))
            msg['X-Original-Subject'] = nettoyer_header(original.get('Subject'))

            body_text = None
            body_html = None

            if original.is_multipart():
                for part in original.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition") or "")
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue

                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            filename_clean = nettoyer_header(filename)
                            msg.add_attachment(payload,
                                               maintype=part.get_content_maintype(),
                                               subtype=part.get_content_subtype(),
                                               filename=filename_clean)
                    elif content_type == "text/html" and not body_html:
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body_html = payload.decode(charset, errors='ignore')
                        except Exception as e:
                            print("Erreur HTML multipart :", e)
                    elif content_type == "text/plain" and not body_text:
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body_text = payload.decode(charset, errors='ignore')
                        except Exception as e:
                            print("Erreur texte multipart :", e)
            else:
                payload = original.get_payload(decode=True)
                charset = original.get_content_charset() or 'utf-8'
                try:
                    decoded = payload.decode(charset, errors='ignore') if payload else ''
                    content_type = original.get_content_type()
                    if content_type == "text/html":
                        body_html = decoded
                    else:
                        body_text = decoded
                except Exception as e:
                    print("Erreur non multipart :", e)

            contenu = EmailMessage()

            if body_html and body_text:
                contenu.set_content(body_text)
                contenu.add_alternative(body_html, subtype='html')
            elif body_html:
                contenu.add_alternative(body_html, subtype='html')
            elif body_text:
                contenu.set_content(body_text)
            else:
                print("⚠ Message vide — ajout du message brut en pièce jointe")
                msg.set_content("Message original joint car vide ou illisible.")
                msg.add_attachment(raw_email, maintype='message', subtype='rfc822')
                continue

            if msg.get_content_maintype() != 'multipart':
                msg.make_mixed()

            for part in contenu.iter_parts():
                msg.attach(part)

            # Vérification de secours : si le message est vide, on reconstruit un message simple
            is_empty = not msg.get_payload() or (
                isinstance(msg.get_payload(), list)
                and all(
                    isinstance(part.get_payload(), bytes) and not part.get_payload()
                    for part in msg.iter_parts()
                    if part.get_content_type().startswith("text/")
                )
            )

            if is_empty:
                print("⚠ Contenu vide détecté — reconstruction d’un message simplifié")
                simple_msg = EmailMessage()
                simple_msg['Subject'] = msg['Subject']
                simple_msg['From'] = msg['From']
                simple_msg['To'] = msg['To']
                simple_msg['Reply-To'] = msg['Reply-To']
                simple_msg['Date'] = msg['Date']
                simple_msg['Message-ID'] = msg['Message-ID']

                if body_text and body_html:
                    simple_msg.set_content(body_text)
                    simple_msg.add_alternative(body_html, subtype='html')
                elif body_html:
                    simple_msg.set_content("Ce message contient uniquement une version HTML.")
                    simple_msg.add_alternative(body_html, subtype='html')
                elif body_text:
                    simple_msg.set_content(body_text)
                else:
                    simple_msg.set_content("Message vide ou non décodable.")

                msg = simple_msg

            # ENVOI VIA SMTP
            print(f"✉️ Envoi du mail : {msg['Subject']}")
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)

            print("✅ OK")
            transferred.append(msg['Subject'])

        imap.logout()
        print(f"\n📬 Total transféré : {len(transferred)} message(s)")
        print(f"⏳ Pause de 5 minutes... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
        time.sleep(300)

    except Exception as e:
        print(f"💥 Erreur : {e}")
        print("⛔ Le script s'arrête. Corrigez le bug avant de relancer.")
        break
