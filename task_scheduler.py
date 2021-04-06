from threading import Thread
import time
import models
from send_email import EmailSender


class TaskScheduller:
    def __init__(self, time_interval: int, mail_login: str, mail_password: str, name_company: str):
        self.time_interval = time_interval
        self.mail_login = mail_login
        self.mail_password = mail_password
        self.name_company = name_company
        self.base_url = 'www.ka-rz.ru/list_tenders/'
        self.stop_thread = False

    def send_notification(self):
        while not self.stop_thread:
            time.sleep(self.time_interval)
            tenders_and_users = models.get_info_closed_tenders_by_interval_time(self.time_interval)

            for tender_and_user in tenders_and_users:
                message = f"""
                <p>Добрый день!</p>
                <p>Благодарим Вас за участие в процедуре {tender_and_user.get('title')} на портале 
                www.ka-rz.ru. В случае, если Ваше ценовое предложение оказалось лучшим специалисты отдела закупок 
                свяжутся с Вами в ближайшее время.</p>
                <p><a href={self.base_url}{tender_and_user.get('url_post')}>Ссылка на прошедшие торги</a></p>
                <p>Ожидаем Вас в будущих процедурах, с уважением к Вам и Вашему делу.</p>
                <p>{self.name_company}</p>
                <p>Внимание, данное сообщение сформировано автоматически и не требует ответа.</p>
                """
                email_sender = EmailSender(self.mail_login, self.mail_password, tender_and_user.get('user_email'),
                                           'Уведомление об аукционе на ka-rz.ru', 'team.ka-rz.ru')
                time.sleep(61)
                email_sender.send_message(message)

    def start_schedule(self):
        thread = Thread(target=self.send_notification, daemon=True)
        thread.start()

    def stop_schedule(self):
        self.stop_thread = True
