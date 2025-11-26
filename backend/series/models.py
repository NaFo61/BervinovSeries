from django.db import models
from django.utils.text import slugify
import os


def series_file_path(instance, filename):
    """Генерирует путь к файлу серии: series/series_slug/season_#/episode_slug.ext"""
    ext = filename.split('.')[-1]
    filename = f"{instance.slug}.{ext}"
    return os.path.join('series', instance.season.series.slug,
                        f'season_{instance.season.number}', filename)


def series_cover_path(instance, filename):
    """Генерирует путь к обложке сериала: covers/series_slug.ext"""
    ext = filename.split('.')[-1]
    filename = f"{instance.slug}.{ext}"
    return os.path.join('covers', filename)


def season_cover_path(instance, filename):
    """Генерирует путь к обложке сезона: covers/series_slug/season_{number}.ext"""
    ext = filename.split('.')[-1]
    filename = f"season_{instance.number}.{ext}"
    return os.path.join('covers', instance.series.slug, filename)


class Series(models.Model):
    """Модель сериала"""

    title = models.CharField(
        max_length=255,
        verbose_name="Название сериала"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug сериала",
        help_text="Уникальный идентификатор для URL"
    )
    description = models.TextField(
        verbose_name="Описание сериала",
        blank=True
    )
    cover_image = models.ImageField(
        upload_to=series_cover_path,
        verbose_name="Обложка сериала",
        blank=True,
        null=True
    )
    release_year = models.PositiveIntegerField(
        verbose_name="Год выхода",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Сериал"
        verbose_name_plural = "Сериалы"
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Автоматическое создание slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Season(models.Model):
    """Модель сезона"""

    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name='seasons',
        verbose_name="Сериал"
    )
    number = models.PositiveIntegerField(
        verbose_name="Номер сезона"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название сезона",
        blank=True
    )
    description = models.TextField(
        verbose_name="Описание сезона",
        blank=True
    )
    cover_image = models.ImageField(
        upload_to=season_cover_path,
        verbose_name="Обложка сезона",
        blank=True,
        null=True
    )
    release_year = models.PositiveIntegerField(
        verbose_name="Год выхода",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"
        ordering = ['series', 'number']
        unique_together = ['series',
                           'number']  # Уникальная комбинация сериал-сезон

    def __str__(self):
        return f"{self.series.title} - Сезон {self.number}"

    def save(self, *args, **kwargs):
        """Автоматическое создание названия сезона если не указано"""
        if not self.title:
            self.title = f"Сезон {self.number}"
        super().save(*args, **kwargs)


class Episode(models.Model):
    """Модель серии"""

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='episodes',
        verbose_name="Сезон"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название серии"
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name="Slug серии"
    )
    number = models.PositiveIntegerField(
        verbose_name="Номер серии в сезоне"
    )
    description = models.TextField(
        verbose_name="Описание серии",
        blank=True
    )
    video_file = models.FileField(
        upload_to=series_file_path,
        verbose_name="Видео файл"
    )
    duration = models.DurationField(
        verbose_name="Длительность",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Серия"
        verbose_name_plural = "Серии"
        ordering = ['season', 'number']
        unique_together = ['season',
                           'slug']  # Уникальный slug в пределах сезона

    def __str__(self):
        return f"{self.season.series.title} S{self.season.number}E{self.number} - {self.title}"

    def save(self, *args, **kwargs):
        """Автоматическое создание slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def series(self):
        """Быстрый доступ к родительскому сериалу"""
        return self.season.series

    def get_absolute_url(self):
        """URL для просмотра серии"""
        from django.urls import reverse
        return reverse('episode_detail', kwargs={
            'series_slug': self.series.slug,
            'season_number': self.season.number,
            'episode_slug': self.slug
        })