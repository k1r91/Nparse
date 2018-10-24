from django.db import models


class Company(models.Model):
    slug = models.SlugField(verbose_name="Abbreviation", unique=True)
    name = models.TextField(max_length=256, verbose_name="Name", blank=True, null=True)
    test = models.TextField(max_length=256, verbose_name="test", blank=True, null=True)
    def __str__(self):
        return "{}".format(self.slug)


class Insider(models.Model):
    name = models.TextField(max_length=256, verbose_name="Name", unique=True)
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    relation = models.TextField(max_length=64, verbose_name="Relation", blank=True, null=True)
    owner_type = models.TextField(max_length=64, verbose_name="Owner type", blank=True, null=True)


class HistoryRecord(models.Model):
    company = models.ForeignKey(Company, verbose_name="Company", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Date", blank=True)
    open = models.FloatField(verbose_name="Open", blank=True, null=True)
    high = models.FloatField(verbose_name="High", blank=True, null=True)
    low = models.FloatField(verbose_name="Low", blank=True, null=True)
    close = models.FloatField(verbose_name="Close/Last", blank=True, null=True)
    volume = models.FloatField(verbose_name="Volume", blank=True, null=True)


class InsiderRecord(models.Model):
    insider = models.ForeignKey(Insider, verbose_name="Insider", on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Date", blank=True)
    shares_traded = models.FloatField(verbose_name="Shares traded", blank=True, null=True)
    last_price = models.FloatField(verbose_name="Last price", blank=True, null=True)
    shares_held = models.FloatField(verbose_name="Shares held", blank=True, null=True)
