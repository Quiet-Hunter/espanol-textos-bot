# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
from send_message import send_message

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Set up a scheduler to run daily at 11:00 UTC
def schedule_daily_message():
    scheduler = BackgroundScheduler()
    timezone = pytz.timezone('UTC')
    scheduler.add_job(send_message, trigger=CronTrigger(hour=11, minute=0, timezone=timezone))
    scheduler.start()
    scheduler.print_jobs()  # Optional: prints scheduled jobs to the log

# Start the scheduler
if __name__ == '__main__':
    schedule_daily_message()

    # Keep the scheduler running
    try:
        while True:
            pass  # Keeps the script running
    except (KeyboardInterrupt, SystemExit):
        pass  # Allow clean exit
