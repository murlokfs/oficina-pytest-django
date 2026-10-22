from django.db import migrations

# O nome fica repetido aqui de propósito: migrations não devem importar código
# da aplicação, porque esse código pode mudar depois e quebrar a migration.
LIBRARIAN_GROUP = "Librarian"


def create_librarian_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=LIBRARIAN_GROUP)


def delete_librarian_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=LIBRARIAN_GROUP).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("library", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_librarian_group, delete_librarian_group),
    ]
