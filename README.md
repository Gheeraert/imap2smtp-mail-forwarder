# imap2smtp-mail-forwarder
Un script Python léger et configurable pour transférer automatiquement les mails récents d’une boîte IMAP vers une autre adresse via SMTP.

# 📬 imap2smtp-mail-forwarder

Un petit script Python pour transférer automatiquement les e-mails non lus récents d'une boîte IMAP vers une autre adresse (SMTP).  
Pensé pour contourner les limitations de redirection imposées par certaines messageries institutionnelles.

---

## ✨ Fonctionnalités

- Connexion sécurisée à une boîte IMAP (université, institution…)
- Recherche automatique des messages **non lus depuis 7 jours**
- Transfert fidèle vers une autre adresse via **SMTP**
- Gestion des pièces jointes, contenus HTML et texte
- Compatible avec **tout serveur IMAP/SMTP** (Gmail, Outlook, Zimbra, etc.)
- Interface 100 % en ligne de commande

---

## 🛠️ Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/imap2smtp-mail-forwarder.git
   cd imap2smtp-mail-forwarder
