from django_extensions.management.jobs import MinutelyJob

class Job(MinutelyJob):
    help = "Hello"

    def execute(self):
        print("HI Worlds")