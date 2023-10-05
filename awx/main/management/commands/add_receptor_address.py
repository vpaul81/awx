# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved

from django.core.management.base import BaseCommand
from django.db import transaction

from awx.main.models import Instance, ReceptorAddress


class Command(BaseCommand):
    """
    Internal tower command.
    Register receptor address to an already-registered instance.
    """

    help = "Add receptor address to an instance."

    def add_arguments(self, parser):
        parser.add_argument('--hostname', dest='hostname', type=str, help="Hostname this address is added to")
        parser.add_argument('--address', dest='address', type=str, help="Receptor address")
        parser.add_argument('--port', dest='port', type=int, help="Receptor listener port")
        parser.add_argument('--protocol', dest='protocol', type=str, default='tcp', choices=['tcp', 'ws'], help="Protocol of the backend connection")
        parser.add_argument('--websocket_path', dest='websocket_path', type=str, default="", help="Path for websockets")
        parser.add_argument('--is_internal', action='store_true', help="If true, address only resolvable within the Kubernetes cluster")

    def _add_address(self, **kwargs):
        try:
            instance = Instance.objects.get(hostname=kwargs.pop('hostname'))
            kwargs['instance'] = instance
            addr = ReceptorAddress.objects.create(**kwargs)
            print(f"Successfully added receptor address {addr.get_full_address()}")
            self.changed = True
        except Exception as e:
            self.changed = False
            print(f"Error adding receptor address: {e}")

    @transaction.atomic
    def handle(self, **options):
        self.changed = False
        address_options = {k: options[k] for k in ('hostname', 'address', 'port', 'protocol', 'websocket_path', 'is_internal')}
        self._add_address(**address_options)
        if self.changed:
            print("(changed: True)")
