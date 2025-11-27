from django.db import models
from django.utils.text import slugify


class Series(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название сериала")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug сериала",
        help_text="Уникальный идентификатор для URL",
    )
    description = models.TextField(verbose_name="Описание сериала", blank=True)
    image = models.ImageField(
        upload_to="series/",
        verbose_name="Обложка сериала",
        blank=True,
        null=True,
    )
    release_year = models.PositiveIntegerField(
        verbose_name="Год выхода", null=True, blank=True
    )

    class Meta:
        verbose_name = "Сериал"
        verbose_name_plural = "Сериалы"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Season(models.Model):
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name="seasons",
        verbose_name="Сериал",
    )
    number = models.PositiveIntegerField(verbose_name="Номер сезона")
    title = models.CharField(
        max_length=255, verbose_name="Название сезона", blank=True
    )
    description = models.TextField(verbose_name="Описание сезона", blank=True)
    image = models.ImageField(
        upload_to="seasons/",
        verbose_name="Обложка сезона",
        blank=True,
        null=True,
    )
    release_year = models.PositiveIntegerField(
        verbose_name="Год выхода", null=True, blank=True
    )

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"
        ordering = ["series", "number"]
        unique_together = [
            "series",
            "number",
        ]  # Уникальная комбинация сериал-сезон

    def __str__(self):
        return f"{self.series.title} - Сезон {self.number}"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Сезон {self.number}"
        super().save(*args, **kwargs)


class Episode(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="episodes",
        verbose_name="Сезон",
    )
    title = models.CharField(max_length=255, verbose_name="Название серии")
    slug = models.SlugField(max_length=255, verbose_name="Slug серии")
    image = models.ImageField(
        upload_to="episodes/",
        verbose_name="Обложка сезона",
        blank=True,
        null=True,
    )
    number = models.PositiveIntegerField(verbose_name="Номер серии в сезоне")
    description = models.TextField(verbose_name="Описание серии", blank=True)

    class Meta:
        verbose_name = "Серия"
        verbose_name_plural = "Серии"
        ordering = ["season", "number"]
        unique_together = [
            "season",
            "slug",
        ]

    def __str__(self):
        return (
            f"{self.season.series.title} "
            f"S{self.season.number}E{self.number} - {self.title}"
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def series(self):
        return self.season.series
