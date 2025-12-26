from django import forms
from django.utils import timezone

from .models import Category, Comment, Location, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "pub_date", "location", "category", "image"]
        widgets = {
            "pub_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "text": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "pub_date": "Если установить дату и время в будущем — можно делать отложенные публикации.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(is_published=True)

        self.fields["location"].queryset = Location.objects.filter(is_published=True)

        if self.instance and self.instance.pub_date:
            self.initial["pub_date"] = self.instance.pub_date.strftime("%Y-%m-%dT%H:%M")
        else:
            self.initial["pub_date"] = timezone.now().strftime("%Y-%m-%dT%H:%M")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Напишите ваш комментарий..."}
            ),
        }
        labels = {
            "text": "",
        }
