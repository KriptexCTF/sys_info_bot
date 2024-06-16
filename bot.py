import telebot
from telebot import types
import logging
import re
import paramiko
import time
import os
import psycopg2

#-----------------------
TOKEN = "your_token"
#-----------------------
host = "host_ip"
port = "22"
username = "username"
password = "password"
#-----------------------
db_host = "db_host"
db_name = "name_db"
postgres_password = "pass_db"
db_user = "postgres"
#-----------------------

logging.basicConfig(filename='bot_logfile.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

#start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Bot started!')

#find_email
@bot.message_handler(commands=['find_email'])
def find_email(message):
    msg = bot.send_message(message.chat.id, 'Пожалуйста, введите текст, в котором нужно найти email адреса:')
    bot.register_next_step_handler(msg, process_text)
def process_text(message):
    text = message.text
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
    if emails:
        bot.send_message(message.chat.id, f'Найдены следующие email адреса:\n{", ".join(emails)}')
        msg = bot.send_message(message.chat.id, 'Добавить ли почты в базу данных? да/нет')
        bot.register_next_step_handler(msg, lambda message: add_emails(message, emails))
    else:
        bot.send_message(message.chat.id, 'Ничего нет!')
def add_emails(message, emails):
    text = message.text
    if(text.upper() == 'ДА'):
        try:
            connection_to_database = psycopg2.connect(dbname=db_name, user=db_user, host=db_host, password=postgres_password, port="5432")
            cur = connection_to_database.cursor()
            for mail in emails:
                cur.execute(f"insert into emails (email) values ('{mail}')")
            connection_to_database.commit()
            cur.close()
            connection_to_database.close()
            bot.send_message(message.chat.id, 'Почты успешно добавлены!')
        except:
            bot.send_message(message.chat.id, 'На одном из этапов произошла ошибка!')
    else:
        bot.send_message(message.chat.id, 'Вы выбрали не добавлять почты!')

#find_phone_number
@bot.message_handler(commands=['find_phone'])
def find_phone(message):
    msg = bot.send_message(message.chat.id, 'Введите текст для поиска номеров телефонов:')
    bot.register_next_step_handler(msg, process_phone_text)
def process_phone_text(message):
    text = message.text
    phones = re.finditer(r"(?:\+?7|8)[ -]?\(?(\d{3})\)?[ -]?(\d{3})[ -]?(\d{2})[ -]?(\d{2})", text)
    formatted_phones = [match.group(0) for match in phones]
    send_results(message, formatted_phones, 'номеров телефонов')
def send_results(message, results, result_type):
    if results:
        bot.send_message(message.chat.id, f'Найдены следующие {result_type}:\n{", ".join(results)}')
        msg = bot.send_message(message.chat.id, 'Добавить ли телефоны в базу данных? да/нет')
        bot.register_next_step_handler(msg, lambda message: add_phones(message, results))
    else:
        bot.send_message(message.chat.id, 'Ничего нет!')
def add_phones(message, results):
    text = message.text
    if(text.upper() == 'ДА'):
        try:
            connection_to_database = psycopg2.connect(dbname=db_name, user=db_user, host=db_host, password=postgres_password, port="5432")
            cur = connection_to_database.cursor()
            for phone in results:
                cur.execute(f"insert into phones (phone) values ('{phone}')")
            connection_to_database.commit()
            cur.close()
            connection_to_database.close()
            bot.send_message(message.chat.id, 'Номера телефонов успешно добавлены!')
        except:
            bot.send_message(message.chat.id, 'На одном из этапов произошла ошибка!')
    else:
        bot.send_message(message.chat.id, 'Вы выбрали не добавлять номера телефонов!')


#verify_password
@bot.message_handler(commands=['verify_password'])
def verify_password(message):
    msg = bot.send_message(message.chat.id, 'Пожалуйста, введите пароль:')
    bot.register_next_step_handler(msg, process_password)
def process_password(message):
    password = message.text
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*().])[A-Za-z\d!@#$%^&*().]{8,}$"
    if re.match(regex, password):
        bot.send_message(message.chat.id, 'Пароль сложный')
    else:
        bot.send_message(message.chat.id, 'Пароль простой')

#get_release
@bot.message_handler(commands=['get_release'])
def get_release(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_uname
@bot.message_handler(commands=['get_uname'])
def get_uname(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    bot.send_message(message.chat.id,data)

#get_uptime
@bot.message_handler(commands=['get_uptime'])
def get_uptime(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_df
@bot.message_handler(commands=['get_df'])
def get_df(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_free
@bot.message_handler(commands=['get_free'])
def get_free(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -m')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_mpstat
@bot.message_handler(commands=['get_mpstat'])
def get_mpstat(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat -A')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_w
@bot.message_handler(commands=['get_w'])
def get_w(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_auths
@bot.message_handler(commands=['get_auths'])
def get_auths(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_critical
@bot.message_handler(commands=['get_critical'])
def get_critical(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -p err..crit -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_ps
@bot.message_handler(commands=['get_ps'])
def get_ps(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_ss
@bot.message_handler(commands=['get_ss'])
def get_ss(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss -a | head')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_apt_list
@bot.message_handler(commands=['get_apt_list'])
def get_apt_list(message):
    msg = bot.send_message(message.chat.id, 'Выберите\n1) Вывести все пакеты\n2) Поиск определенного пакета')
    bot.register_next_step_handler(msg, process_apt)
def process_apt(message):
    text = message.text
    if(text == '1'):
        all_apt(message)
    elif(text == '2'):
        name_apt(message)
    else:
        bot.send_message(message.chat.id,"Неверная опция!")
def all_apt(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('apt list | head')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)
def name_apt(message):
    msg = bot.send_message(message.chat.id, 'Введите название пакета')
    bot.register_next_step_handler(msg, process_name_apt)
def process_name_apt(message):
    text = message.text
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('apt-cache show ' + text)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    bot.send_message(message.chat.id,data)

#get_services
@bot.message_handler(commands=['get_services'])
def get_services(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl | head')
    data = stdout.read() + stderr.read()
    client.close()
    bot.send_message(message.chat.id,data)

#get_repl_logs
@bot.message_handler(commands=['get_repl_logs'])
def get_repl_logs(message):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-16-main.log | grep REPLICATION')
    data = stdout.read() + stderr.read()
    client.close()
    bot.send_message(message.chat.id,data)

#get_emails
@bot.message_handler(commands=['get_emails'])
def get_emails(message):
    connection_to_database = psycopg2.connect(dbname=db_name, user=db_user, host=db_host, password=postgres_password, port="5432")
    cur = connection_to_database.cursor()
    cur.execute("SELECT * FROM emails")
    data = cur.fetchall()
    result = ""
    for i in range(len(data)):
        result += str(data[i][1]) + '\n'
    bot.send_message(message.chat.id, result)
    cur.close()
    connection_to_database.close()

#get_phone_numbers
@bot.message_handler(commands=['get_phone_numbers'])
def get_phone_numbers(message):
    connection_to_database = psycopg2.connect(dbname=db_name, user=db_user, host=db_host, password=postgres_password, port="5432")
    cur = connection_to_database.cursor()
    cur.execute("SELECT * FROM phones")
    data = cur.fetchall()
    result = ""
    for i in range(len(data)):
        result += str(data[i][1]) + '\n'
    bot.send_message(message.chat.id, result)
    cur.close()
    connection_to_database.close()

#Bot start
bot.polling()