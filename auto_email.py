'''
使用qq邮箱自动发送邮件

这两个库都无法直接使用pip install安装,使用以下两行命令即可安装

pip install PyEmail
easy_install email
'''

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
 
my_sender='xxx@qq.com'
my_pass = 'xxx'   
my_user='xxx@qq.com'   
def send_email(sender_email, sender_password, receiver_email, content = "", title = "无标题", nickname = None):
    try:
        msg = MIMEText(content,'plain','utf-8')
        msg['From'] = formataddr([nickname if nickname != None else sender_email, sender_email])
        msg['To'] = formataddr(["", receiver_email])              
        msg['Subject'] = title

        server=smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,[receiver_email,],msg.as_string())
        server.quit()
    except Exception as e:
        print(e)
        return False
    return True

send_email(my_sender, my_pass, my_user, "hello world", "hello world", "")
