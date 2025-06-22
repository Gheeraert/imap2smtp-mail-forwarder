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
- Le script fonctionne en boucle, avec un délai de 5 minutes entre chaque synchronisation. Pour une exécution ponctuelle, décommentez simplement la dernière ligne et commentez la boucle while.
- Les identifiants sont saisis dynamiquement à l’exécution, et ne sont jamais stockés.
- Pour Gmail, pensez à générer un mot de passe d'application (https://support.google.com/accounts/answer/185833)

---

## 📄Licence
Ce script est distribué sous licence MIT.
Liberté totale d’usage, de modification et de diffusion.

## 🛠️ Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/imap2smtp-mail-forwarder.git
   cd imap2smtp-mail-forwarder
