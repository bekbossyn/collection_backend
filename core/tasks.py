import celery
import threading

from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage
from django.conf import settings

from utils.string_utils import valid_email

from celery.task import periodic_task

logger = get_task_logger(__name__)


@celery.task(default_retry_delay=2 * 10, max_retries=2)
def email(to, subject, message):
    """
    Sends email to user/users. 'to' parameter must be a string or list.
    """
    # Converto to list if one user's email is passed
    if not isinstance(to, list):  # Python 2.x only
        to = [to]
    try:
        email_list = list(filter(lambda email: valid_email(email), to))
        # msg = EmailMessage(subject, message,
        #                    from_email=settings.FROM_EMAIL,
        #                    to=email_list)
        # msg.content_subtype = "html"
        # msg.send()
        send_html_mail(subject, message, to)
    except Exception as exc:
        print(exc)
        raise email.retry(exc=exc)


class EmailThread(threading.Thread):

    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(
            self.subject, self.html_content,
            from_email=settings.FROM_EMAIL, to=self.recipient_list)
        msg.content_subtype = "html"
        msg.send()


def send_html_mail(subject, html_content, recipient_list):
    EmailThread(subject, html_content, recipient_list).start()


numbers = []
for x in range(0, 10):
    numbers.append(str(x))

doubles = numbers
doubles.append(".")

kazakh_doubles = numbers
kazakh_doubles.append(",")


def clear_rate(current_rate):
    """
        Gets rid of commas in numbers inside the string
    """
    while "," in current_rate:
        ind = current_rate.find(",")
        current_rate = current_rate[:ind] + current_rate[(ind + 1):]
    return current_rate


def convert_to_list_rate(current_rate):
    """
        Gets list of organized floats from the string
    """
    current_rate = current_rate[55:]
    my_list = []
    head = -1
    tail = -1
    for i in range(5):
        for j in range(len(current_rate)):
            if current_rate[j] in doubles:
                head = j
                break

        for j in range(head + 1, len(current_rate)):
            if current_rate[j] not in doubles:
                tail = j - 1
                break

        number = current_rate[head: (tail + 1)]
        my_list.append(float(number))
        current_rate = current_rate[(tail + 1):]
    return my_list


def previous_date_fn(year, month, day):

    year_int = int(year)
    month_int = int(month)
    day_int = int(day)

    import datetime
    today = datetime.date(year_int, month_int, day_int)

    yesterday = today - datetime.timedelta(days=1)

    day = str(yesterday.day)

    if len(day) < 2:
        day = '0' + day
    month = str(yesterday.month)
    if len(month) < 2:
        month = '0' + month
    year = str(yesterday.year)
    return year, month, day


@periodic_task(run_every=(crontab(minute=1)))
# @celery.task(default_retry_delay=180, max_retries=None)
def converter_task():
    """
    update info each period of time.
    converter task
    """
    import datetime
    from core.models import Exchange

    now = datetime.datetime.now()
    delta = datetime.timedelta(hours=9)
    now = now + delta

    five_minutes = datetime.timedelta(minutes=5)
    last_object = Exchange.objects.last()
    last_object_time = last_object.timestamp

    from utils.time_utils import dt_to_timestamp
    if dt_to_timestamp((now - five_minutes)) < dt_to_timestamp(last_object_time):
        return last_object.json()
    # Otherwise return the NEW PARSED RESULT
    new_now = datetime.datetime.now() + datetime.timedelta(hours=9)
    year = str(new_now.year)
    month = '{:02d}'.format(new_now.month)
    day = '{:02d}'.format(new_now.day)

    import requests
    payload = {'BAS_DT': year + month + day,
               'NAT_CODE': 'USD',
               'DIS': 1,
               'INQ_DIS': 'USD',
               }

    url = 'https://spib.wooribank.com/spd/jcc?withyou=ENENG0432&__ID=c010895'

    response = requests.post(
        url=url,
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    result = response.text

    l = result.index("<dd>") + len("<dd>")
    current_year = result[l:(l + 4)]
    current_month = result[(l + 5):(l + 7)]
    current_day = result[(l + 8):(l + 10)]

    payload = {'BAS_DT': current_year + current_month + current_day,
               'NAT_CODE': 'USD',
               'DIS': 1,
               'INQ_DIS': 'USD',
               }

    response = requests.post(
        url=url,
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    while response.text.find("Currently, there is no notification. Please try again late.") > 0:
        current_year, current_month, current_day = previous_date_fn(current_year, current_month, current_day)

        data = {'BAS_DT': current_year + current_month + current_day,
                'NAT_CODE': 'USD',
                'DIS': 1,
                'INQ_DIS': 'USD',
                }

        response = requests.post(
            url=url,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

    result = response.text

    body = result[(result.index("<tbody>") + len("<tbody>")):result.index("</tbody>")]

    row = body[(body.index("<tr>") + len("<tr>")):(body.index("</tr>"))]

    while row.find(",") > 0:
        row = row[:row.find(",")] + row[row.find(",") + 1:]

    row = row[row.find("</td>") + len("</td>"):]
    row = row[row.find("<td>") + len("<td>"):]

    j = 0
    while row[j] not in doubles:
        j = j + 1
    current_time = row[j:j + 8]
    row = row[(j + 8):]
    row = row[row.index("<td>") + len("<td>"):]

    j = 0
    while row[j] not in doubles:
        j = j + 1
    k = j
    while row[k] in doubles:
        k = k + 1

    #############################################################################################
    url = "https://ifin.kz/bank/halykbank/currency-rate/astana"
    response = requests.get(
        url=url,
        params=None,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    result = response.text

    body = result[(result.index("tbl-td rate-value")):(result.index("tbl-td rate-value") + 200)]
    body = body[body.index(">"):]

    kj = 0
    while body[kj] not in kazakh_doubles:
        kj = kj + 1
    kk = kj
    while body[kk] in kazakh_doubles:
        kk = kk + 1
    body_copy = body
    for iii in range(kj, kk):
        if body_copy[iii] == ',':
            body_copy[iii] = "."

    receiving = float(body[kj:kk])

    #############################################################################################

    sending = float(row[j:k])
    last_exchange = Exchange.objects.last()
    last_exchange.sending = sending
    last_exchange.receiving = receiving
    last_exchange.data_and_time = current_day + "." + current_month + "." + current_year + " " + current_time
    last_exchange.timestamp = new_now
    last_exchange.save()

