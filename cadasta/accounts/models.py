from buckets.fields import S3FileField
from datetime import datetime, timezone, timedelta
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
import django.contrib.auth.models as auth
import django.contrib.auth.base_user as auth_base
from allauth.account.signals import password_changed, password_reset
from tutelary.models import Policy
from tutelary.decorators import permissioned_model
from django_otp.models import Device
from django_otp.oath import TOTP
from django_otp.util import random_hex, hex_validator
from binascii import unhexlify

import time

from simple_history.models import HistoricalRecords
from .manager import UserManager
from .utils import send_sms
from . import messages as account_message

PERMISSIONS_DIR = settings.BASE_DIR + '/permissions/'


def now_plus_48_hours():
    return datetime.now(tz=timezone.utc) + timedelta(hours=48)


def abstract_user_field(name):
    for f in auth.AbstractUser._meta.fields:
        if f.name == name:
            return f


@permissioned_model
class User(auth_base.AbstractBaseUser, auth.PermissionsMixin):
    username = abstract_user_field('username')
    full_name = models.CharField(_('full name'), max_length=130, blank=True)
    email = models.EmailField(
        _('email address'), blank=True, null=True, default=None, unique=True
    )
    phone = models.CharField(
        _('phone number'), max_length=16, null=True,
        blank=True, default=None, unique=True
    )
    is_staff = abstract_user_field('is_staff')
    is_active = abstract_user_field('is_active')
    date_joined = abstract_user_field('date_joined')
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    update_profile = models.BooleanField(default=True)
    language = models.CharField(max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    measurement = models.CharField(max_length=20,
                                   choices=settings.MEASUREMENTS,
                                   default=settings.MEASUREMENT_DEFAULT)
    avatar = S3FileField(upload_to='avatars',
                         accepted_types=settings.ACCEPTED_AVATAR_TYPES,
                         blank=True)

    objects = UserManager()

    # Audit history
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()
    _dict_languages = dict(settings.LANGUAGES)
    _dict_measurements = dict(settings.MEASUREMENTS)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()

    class TutelaryMeta:
        perm_type = 'user'
        path_fields = ('username',)
        actions = [('user.list',
                    {'permissions_object': None,
                     'error_message':
                     _("You don't have permission to view user details")}),
                   ('user.update',
                    {'error_message':
                     _("You don't have permission to update user details")})]

    def __repr__(self):
        repr_string = ('<User username={obj.username}'
                       ' full_name={obj.full_name}'
                       ' email={obj.email}'
                       ' email_verified={obj.email_verified}'
                       ' phone={obj.phone}'
                       ' phone_verified={obj.phone_verified}>')
        return repr_string.format(obj=self)

    def get_display_name(self):
        """
        Returns the display name.
        If full name is present then return full name as display name
        else return username.
        """
        if self.full_name != '':
            return self.full_name
        else:
            return self.username

    @property
    def avatar_url(self):
        if not self.avatar or not self.avatar.url:
            return settings.DEFAULT_AVATAR
        return self.avatar.url

    @property
    def language_verbose(self):
        language_code = self.language.split('-')[0]
        return self._dict_languages[language_code]

    @property
    def measurement_verbose(self):
        return self._dict_measurements[self.measurement]


@receiver(models.signals.post_save, sender=User)
def assign_default_policy(sender, instance, created, **kwargs):
    if not created:
        return
    instance.assign_policies(Policy.objects.get(name='default'))


@receiver(password_changed)
@receiver(password_reset)
def password_changed_reset(sender, request, user, **kwargs):
    msg_body = render_to_string(
        'accounts/email/password_changed_notification.txt')
    if user.email:
        send_mail(
            _("Change of password at Cadasta Platform"),
            msg_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
    if user.phone:
        send_sms(user.phone, account_message.password_change_or_reset)


def default_key():
    return random_hex(20).decode()


class VerificationDevice(Device):
    unverified_phone = models.CharField(max_length=16)
    secret_key = models.CharField(
        max_length=40,
        default=default_key,
        validators=[hex_validator],
        help_text="Hex-encoded secret key to generate totp tokens.",
        unique=True,
    )
    last_verified_counter = models.BigIntegerField(
        default=-1,
        help_text=("The counter value of the latest verified token."
                   "The next token must be at a higher counter value."
                   "It makes sure a token is used only once.")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=20,
                             choices=(('phone_verify', _("Verify Phone")),
                                      ('password_reset', _("Reset Password"))),
                             default='phone_verify')
    verified = models.BooleanField(default=False)

    step = settings.TOTP_TOKEN_VALIDITY
    digits = settings.TOTP_DIGITS

    class Meta(Device.Meta):
        verbose_name = "Verification Device"

    @property
    def bin_key(self):
        return unhexlify(self.secret_key.encode())

    def totp_obj(self):
        totp = TOTP(key=self.bin_key, step=self.step, digits=self.digits)
        totp.time = time.time()
        return totp

    def generate_challenge(self):
        totp = self.totp_obj()
        token = str(totp.token()).zfill(self.digits)

        message = _("Your token for Cadasta is {token_value}."
                    " It is valid for {time_validity} minutes.")
        message = message.format(
            token_value=token, time_validity=self.step // 60)

        send_sms(to=self.unverified_phone, body=message)

        return token

    def verify_token(self, token, tolerance=0):
        totp = self.totp_obj()
        if ((totp.t() > self.last_verified_counter) and
                (totp.verify(token, tolerance=tolerance))):
            self.last_verified_counter = totp.t()
            self.verified = True
            self.save()
        else:
            self.verified = False
        return self.verified
