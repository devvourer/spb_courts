from django.db import models


class Court(models.Model):
    class ParityChoices(models.TextChoices):
        UNEVEN = '-1', 'нечетные'
        EVEN = '1', 'четные'
        ALL = '0', 'все'

    code_GASRF = models.CharField(max_length=50, null=True)
    site = models.URLField(null=True)
    region = models.CharField(max_length=250, null=True, verbose_name="Регион")
    district = models.CharField(max_length=250, null=True, verbose_name='Район')

    name_judicial_precinct = models.CharField(max_length=250, null=True, verbose_name='Наименование судебного участка')
    address = models.CharField(max_length=250, null=True)

    judge_full_name = models.CharField(max_length=250, null=True, verbose_name='ФИО Судьи')
    judge_email = models.EmailField(null=True)

    assistant_full_name = models.CharField(max_length=250, null=True, verbose_name='ФИО Помощника Судьи')

    clerk_full_name = models.CharField(max_length=250, null=True, verbose_name='ФИО Секретаря судебного участка')

    secretary_court_session = models.CharField(max_length=250, null=True, verbose_name='Секретаря судебного заседания')

    type_phone_1 = models.CharField(max_length=25, null=True)
    phone_1 = models.CharField(max_length=25, null=True)

    type_phone_2 = models.CharField(max_length=25, null=True)
    phone_2 = models.CharField(max_length=25, null=True)

    type_phone_3 = models.CharField(max_length=25, null=True)
    phone_3 = models.CharField(max_length=25, null=True)


class Jurisdiction(models.Model):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='jurisdictions')

    district = models.CharField(max_length=250, null=True,
                                  verbose_name='Район, населенный пункт')
    street = models.CharField(max_length=250, null=True,
                              verbose_name='микрорайон, улица, прочие адресные указатели')
    house_number = models.CharField(max_length=6, null=True,
                                    verbose_name='номер дома, если в подсудность входят единичные дома')

    start_house_number = models.CharField(max_length=6, null=True,
                                          verbose_name='номер дома начала интервала')
    end_house_number = models.CharField(max_length=6, null=True, verbose_name='номер дома конца интервала')
    parity = models.CharField(max_length=2, null=True)
    excluded_houses = models.CharField(max_length=250, null=True)
