import pytest
import yaml

from django.db.utils import IntegrityError

from awx.api.versioning import reverse
from awx.main.models import Instance
from awx.api.views.instance_install_bundle import generate_group_vars_all_yml


@pytest.mark.django_db
def test_prevent_peering_to_self(control_instance):
    '''
    cannot peer to self
    '''
    with pytest.raises(IntegrityError):
        control_instance.peers.add(control_instance)


@pytest.mark.django_db
@pytest.mark.parametrize('node_type', ['control', 'hop', 'execution'])
def test_creating_node(node_type, admin_user, post):
    '''
    can only add hop and execution nodes via API
    '''
    r = post(
        url=reverse('api:instance_list'),
        data={"hostname": "abc", "node_type": node_type},
        user=admin_user,
        expect=400 if node_type == 'control' else 201,
    )


@pytest.mark.django_db
def test_changing_node_type(admin_user, patch):
    '''
    cannot change node type
    '''
    hop = Instance.objects.create(hostname='abc', node_type="hop")
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': hop.pk}),
        data={"node_type": "execution"},
        user=admin_user,
        expect=400,
    )


@pytest.mark.django_db
@pytest.mark.parametrize('node_type', ['hop', 'execution'])
def test_listener_port_null(node_type, admin_user, post):
    '''
    listener_port can be None
    '''
    r = post(
        url=reverse('api:instance_list'),
        data={"hostname": "abc", "node_type": node_type, "listener_port": None},
        user=admin_user,
        expect=201,
    )


@pytest.mark.django_db
@pytest.mark.parametrize('node_type, allowed', [('control', False), ('hop', True), ('execution', True)])
def test_peers_from_control_nodes_allowed(node_type, allowed, post, admin_user):
    '''
    only hop and execution nodes can have peers_from_control_nodes set to True
    '''
    r = post(
        url=reverse('api:instance_list'),
        data={"hostname": "abc", "peers_from_control_nodes": True, "node_type": node_type, "listener_port": 6789},
        user=admin_user,
        expect=201 if allowed else 400,
    )


@pytest.mark.django_db
def test_listener_port_is_required(admin_user, post):
    '''
    if adding instance to peers list, that instance must have listener_port set
    '''
    hop = Instance.objects.create(hostname='abc', node_type="hop", listener_port=None)
    r = post(
        url=reverse('api:instance_list'),
        data={"hostname": "ex", "peers_from_control_nodes": False, "node_type": "execution", "listener_port": None, "peers": ["abc"]},
        user=admin_user,
        expect=400,
    )


@pytest.mark.django_db
def test_peers_from_control_nodes_listener_port_enabled(admin_user, post):
    '''
    if peers_from_control_nodes is True, listener_port must an integer
    Assert that all other combinations are allowed
    '''
    control = Instance.objects.create(hostname='abc', node_type="control")
    i = 0
    for node_type in ['hop', 'execution']:
        for peers_from in [True, False]:
            for listener_port in [None, 6789]:
                # only disallowed case is when peers_from is True and listener port is None
                disallowed = peers_from and not listener_port
                r = post(
                    url=reverse('api:instance_list'),
                    data={"hostname": f"abc{i}", "peers_from_control_nodes": peers_from, "node_type": node_type, "listener_port": listener_port},
                    user=admin_user,
                    expect=400 if disallowed else 201,
                )
                i += 1


@pytest.mark.django_db
def test_disallow_modify_peers_control_nodes(admin_user, patch):
    '''
    for control nodes, peers field should not be
    modified directly via patch.
    '''
    control = Instance.objects.create(hostname='abc', node_type='control')
    hop1 = Instance.objects.create(hostname='hop1', node_type='hop', peers_from_control_nodes=True, listener_port=6789)
    hop2 = Instance.objects.create(hostname='hop2', node_type='hop', peers_from_control_nodes=False, listener_port=6789)
    assert [hop1] == list(control.peers.all())  # only hop1 should be peered
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': control.pk}),
        data={"peers": ["hop2"]},
        user=admin_user,
        expect=400,  # cannot add peers directly
    )
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': control.pk}),
        data={"peers": ["hop1"]},
        user=admin_user,
        expect=200,  # patching with current peers list should be okay
    )
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': control.pk}),
        data={"peers": []},
        user=admin_user,
        expect=400,  # cannot remove peers directly
    )
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': control.pk}),
        data={},
        user=admin_user,
        expect=200,  # patching without data should be fine too
    )
    # patch hop2
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': hop2.pk}),
        data={"peers_from_control_nodes": True},
        user=admin_user,
        expect=200,  # patching without data should be fine too
    )
    control.refresh_from_db()
    assert {hop1, hop2} == set(control.peers.all())  # hop1 and hop2 should now be peered from control node


@pytest.mark.django_db
def test_disallow_changing_hostname(admin_user, patch):
    '''
    cannot change hostname
    '''
    hop = Instance.objects.create(hostname='hop', node_type='hop')
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': hop.pk}),
        data={"hostname": "hop2"},
        user=admin_user,
        expect=400,
    )


@pytest.mark.django_db
def test_disallow_changing_node_state(admin_user, patch):
    '''
    only allow setting to deprovisioning
    '''
    hop = Instance.objects.create(hostname='hop', node_type='hop', node_state='installed')
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': hop.pk}),
        data={"node_state": "deprovisioning"},
        user=admin_user,
        expect=200,
    )
    r = patch(
        url=reverse('api:instance_detail', kwargs={'pk': hop.pk}),
        data={"node_state": "ready"},
        user=admin_user,
        expect=400,
    )


@pytest.mark.django_db
def test_control_node_automatically_peers():
    '''
    a new control node should automatically
    peer to hop

    peer to hop should be removed if hop is deleted
    '''

    hop = Instance.objects.create(hostname='hop', node_type='hop', peers_from_control_nodes=True, listener_port=6789)
    control = Instance.objects.create(hostname='abc', node_type='control')
    assert hop in control.peers.all()
    hop.delete()
    assert not control.peers.exists()


@pytest.mark.django_db
def test_group_vars(get, admin_user):
    '''
    control > hop1 > hop2 < execution
    '''
    control = Instance.objects.create(hostname='control', node_type='control', listener_port=None)
    hop1 = Instance.objects.create(hostname='hop1', node_type='hop', listener_port=6789, peers_from_control_nodes=True)
    hop2 = Instance.objects.create(hostname='hop2', node_type='hop', listener_port=6789, peers_from_control_nodes=False)
    execution = Instance.objects.create(hostname='execution', node_type='execution', listener_port=6789)

    execution.peers.add(hop2)
    hop1.peers.add(hop2)

    control_vars = yaml.safe_load(generate_group_vars_all_yml(control))
    hop1_vars = yaml.safe_load(generate_group_vars_all_yml(hop1))
    hop2_vars = yaml.safe_load(generate_group_vars_all_yml(hop2))
    execution_vars = yaml.safe_load(generate_group_vars_all_yml(execution))

    def has_peer(group_vars, peer):
        peers = group_vars.get('receptor_peers', [])
        for p in peers:
            if f"{p['host']}:{p['port']}" == peer:
                return True
        return False

    # control group vars assertions
    assert control_vars.get('receptor_host_identifier', '') == 'control'
    assert has_peer(control_vars, 'hop1:6789')
    assert not has_peer(control_vars, 'hop2:6789')
    assert not has_peer(control_vars, 'execution:6789')
    assert not control_vars.get('receptor_listener', False)

    # hop1 group vars assertions
    assert hop1_vars.get('receptor_host_identifier', '') == 'hop1'
    assert has_peer(hop1_vars, 'hop2:6789')
    assert not has_peer(hop1_vars, 'execution:6789')
    assert hop1_vars.get('receptor_listener', False)

    # hop2 group vars assertions
    assert hop2_vars.get('receptor_host_identifier', '') == 'hop2'
    assert not has_peer(hop2_vars, 'hop1:6789')
    assert not has_peer(hop2_vars, 'execution:6789')
    assert hop2_vars.get('receptor_listener', False)
    assert hop2_vars.get('receptor_peers', []) == []

    # execution group vars assertions
    assert execution_vars.get('receptor_host_identifier', '') == 'execution'
    assert has_peer(execution_vars, 'hop2:6789')
    assert not has_peer(execution_vars, 'hop1:6789')
    assert execution_vars.get('receptor_listener', False)
