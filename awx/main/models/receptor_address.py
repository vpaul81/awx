from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from awx.api.versioning import reverse
from django.db.models import Sum, Q


class ReceptorAddress(models.Model):
    class Meta:
        app_label = 'main'
        constraints = [
            models.UniqueConstraint(
                fields=["address", "protocol"],
                name="unique_receptor_address",
                violation_error_message=_("Receptor address + protocol must be unique."),
            )
        ]

    address = models.CharField(max_length=255)
    port = models.IntegerField(default=27199, validators=[MinValueValidator(0), MaxValueValidator(65535)])
    protocol = models.CharField(max_length=10, default="tcp")
    websocket_path = models.CharField(max_length=255, default="", blank=True)
    is_internal = models.BooleanField(default=False)
    peers_from_control_nodes = models.BooleanField(default=False)
    instance = models.ForeignKey(
        'Instance',
        related_name='receptor_addresses',
        on_delete=models.CASCADE,
    )

    def get_full_address(self):
        scheme = ""
        path = ""
        port = ""
        if self.protocol == "ws":
            scheme = "wss://"

        if self.protocol == "ws" and self.websocket_path:
            path = f"/{self.websocket_path}"

        if self.port:
            port = f":{self.port}"

        return f"{scheme}{self.address}{port}{path}"

    def get_peer_type(self):
        if self.protocol == 'tcp':
            return 'tcp-peer'
        elif self.protocol in ['ws', 'wss']:
            return 'ws-peer'
        else:
            return None

    def get_absolute_url(self, request=None):
        return reverse('api:receptor_address_detail', kwargs={'pk': self.pk}, request=request)
