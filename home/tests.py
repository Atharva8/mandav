from django.test import TestCase
from home.models import ItemInst, Order, Customer, Item
from django.utils import timezone
import datetime

class ModelTestCase(TestCase):
    def setUp(self) -> None:
        Customer.create.