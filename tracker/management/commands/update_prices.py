import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from tracker.models import Product
from tracker.scraper import getRozetkaPrice

class Command(BaseCommand):
    help = 'Автоматично оновлює ціни для всіх товарів у базі даних'
    def send_telegram_message(self, text):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={settings.TELEGRAM_CHAT_ID}&text={text}"
        requests.get(url)
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        self.stdout.write(f"Знайдено товарів у базі: {products.count()}")
        for product in products:
            self.stdout.write(f"Перевіряю ціну для: {product.name}...")
            if 'rozetka.com.ua' in product.url:
                new_price = getRozetkaPrice(product.url)
                if new_price:
                    if product.currentPrice != new_price:
                        msg = f"Увага! Змінилася ціна на {product.name}!\nБуло: {product.currentPrice} грн\nСтало: {new_price} грн\nПосилання: {product.url}"
                        self.send_telegram_message(msg)
                    product.currentPrice = new_price
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f"Успіх! Нова ціна: {new_price} грн"))
                else:
                    self.stdout.write(self.style.ERROR(f"Не вдалося отримати ціну для {product.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Парсер для цього магазину ще не написаний."))