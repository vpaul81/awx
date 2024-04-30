from collections import defaultdict
import sys

from django.contrib.contenttypes.models import ContentType

from awx.main.fields import ImplicitRoleField
from awx.main.models.rbac import Role


crosslinked = defaultdict(lambda: defaultdict(dict))
orphaned_roles = []


for ct in ContentType.objects.order_by('id'):
    cls = ct.model_class()
    if not any(isinstance(f, ImplicitRoleField) for f in cls._meta.fields):
        continue
    for obj in cls.objects.all():
        for f in cls._meta.fields:
            if not isinstance(f, ImplicitRoleField):
                continue
            r = getattr(obj, f.name, None)
            if not r:
                sys.stderr.write(f"{cls} id={obj.id} {f.name} does not have a Role object\n")
                crosslinked[ct.id][obj.id][f'{f.name}_id'] = None
                continue
            if r.content_object != obj:
                sys.stderr.write(f"{cls.__name__} id={obj.id} {f.name} is pointing to a Role that is assigned to a different object: role.id={r.id} {r.content_type!r} {r.object_id} {r.role_field}\n")
                crosslinked[ct.id][obj.id][f'{f.name}_id'] = None
                continue


sys.stderr.write('===================================\n')
for r in Role.objects.exclude(role_field__startswith='system_').order_by('id'):
    if not r.content_object:
        sys.stderr.write(f"Role id={r.id} is missing a valid content_object: {r.content_type!r} {r.object_id} {r.role_field}\n")
        orphaned_roles.append(r.id)
        continue
    rev = getattr(r.content_object, r.role_field, None)
    if not rev:
        continue
    if r.id != rev.id:
        sys.stderr.write(f"Role id={r.id} {r.content_type!r} {r.object_id} {r.role_field} is pointing to an object using a different role: id={rev.id} {rev.content_type!r} {rev.object_id} {rev.role_field}\n")
        crosslinked[r.content_type_id][r.object_id][f'{r.role_field}_id'] = r.id
        continue


sys.stderr.write('===================================\n')


print(f"""\
from django.contrib.contenttypes.models import ContentType

from awx.main.models.rbac import Role, batch_role_ancestor_rebuilding

""")

print("# Role objects that are assigned to objects that do not exist")
for r in orphaned_roles:
    print(f"Role.objects.filter(id={r}).delete()")


print("\n")
print("# Resource objects that are pointing to the wrong Role.  Some of these")
print("# do not have corresponding Roles anywhere, so delete the foreign key.")
print("# For those, new Roles will be constructed upon save.\n")
print("queue = []\n")
for ct, objs in crosslinked.items():
    print(f"cls = ContentType.objects.get(id={ct}).model_class()\n")
    for obj, kv in objs.items():
        print(f"cls.objects.filter(id={obj}).update(**{kv!r})")
        print(f"queue.append((cls, {obj}))")

print(f"\nwith batch_role_ancestor_rebuilding():")
print(f"    for cls, obj_id in queue:")
print(f"        obj = cls.objects.get(id=obj_id)")
print(f"        obj.save()")
