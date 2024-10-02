import smtplib

to = 'alenoshan@gmail.com'
gmail_user = 'shehankirsten@gmail.com'
gmail_pwd = 'vaejmoibhpvaltzk'


class AlertMail:
    def __init__(self, medi):
        self.medi = medi
        
    def send_alert(self, medi):
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmail_user, gmail_pwd)
        header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Failed to take medicine \n'

        msg = header + f'\n You missed your medicine: {self.medi}\n\n'
        smtpserver.sendmail(gmail_user, to, msg)

        smtpserver.quit()
