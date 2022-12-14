import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=17, blank=True)
    display_name = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_name and self.phone_number:
            self.display_name = self.phone_number
        elif not self.display_name and not self.phone_number:
            self.display_name = self.username
        super(User, self).save(*args, **kwargs)


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    members = models.ManyToManyField(User)
    private = models.BooleanField(blank=False, default=False)
    display_name = models.CharField(max_length=150, blank=True)
    audio_file_creator = models.CharField(default="", max_length=150, blank=True)
    audio_file_created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.id
        room = Room.objects.filter(id=self.id).first()
        if room:
            room_members = set(
                [user["username"] for user in room.members.all().values("username")]
            )
        else:
            room_members = set()
        if self.audio_file_creator and self.audio_file_creator not in room_members:
            raise ValidationError(_(f"File creator must have username of room member."))
        super(Room, self).save(*args, **kwargs)


class JoinRequest(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        other_requests = JoinRequest.objects.filter(
            user=self.user, room=self.room
        ).exclude(id=self.id)
        if other_requests.exists():
            raise ValidationError(_("Join request must be unique per user in room."))
        super(JoinRequest, self).save(*args, **kwargs)


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    audio_uploaded_by = models.ForeignKey(
        User, null=True, related_name="user_uploading_audio", on_delete=models.CASCADE
    )
    read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        other_notifications = Notification.objects.filter(
            user=self.user, room=self.room
        ).exclude(id=self.id)
        if other_notifications.exists():
            raise ValidationError(_("Notification must be unique per user in room."))
        super(Notification, self).save(*args, **kwargs)
