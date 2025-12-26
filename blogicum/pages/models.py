from core.constans import MAX_LENGTH
from django.db import models
from django.utils.text import slugify


class StaticPage(models.Model):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH)
    content = models.TextField("Содержание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.",
    )
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "статичная страница"
        verbose_name_plural = "Статичные страницы"
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
