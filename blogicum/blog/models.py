from core.constans import LENGTH_STRING, MAX_LENGTH
from core.models import IsPublishedCreatedAt
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

tz = timezone.now()
tr = True


class PublishedQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.select_related("category", "location", "author").filter(
            pub_date__lte=now, is_published=True, category__is_published=True
        )


class Category(IsPublishedCreatedAt):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; разрешены символы "
        "латиницы, цифры, дефис и подчёркивание.",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:LENGTH_STRING]


class Location(IsPublishedCreatedAt):
    name = models.CharField("Название места", max_length=MAX_LENGTH)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:LENGTH_STRING]


class Post(IsPublishedCreatedAt):
    title = models.CharField("Заголовок", max_length=MAX_LENGTH)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату и время в будущем"
        " — можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="posts",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="posts_images/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)

    objects = PublishedQuerySet.as_manager()

    def __str__(self):
        return self.title[:LENGTH_STRING]

    @property
    def comment_count(self):
        """Количество комментариев к посту."""
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Публикация",
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comments",
    )
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField(
        "Дата и время создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self):
        return f"Комментарий от {self.author} к посту {self.post.title}"
