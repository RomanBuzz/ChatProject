from django.db import models
from PIL import Image
from django.contrib.auth.models import User


class ChatUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField("Аватар", max_length=None, upload_to='avatars/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    def __str__(self):
        return self.user.username


class Room(models.Model):
    name = models.CharField(max_length=255)
    online = models.ManyToManyField(to=User, blank=True)

    @property
    def get_online_count(self):
        # используем свойство для передачи имя комнаты и количества пользователей в веб-сокет
        return f'{self.name} ({self.online.count()})'

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return self.get_online_count


class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.timestamp.strftime("%d.%m.%Y %H:%M:%S")}] {self.user.username}: {self.content}'
