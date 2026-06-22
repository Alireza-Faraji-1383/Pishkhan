# Generated for email-based authentication refactor

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_options_alter_verificationcode_options'),
    ]

    operations = [
        # Switch the default manager from UserManager to CustomUserManager
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
        # Remove the username field (email is now the unique identifier)
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        # Make email unique and required (was optional/blank before)
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='ایمیل'),
        ),
        # Remove the global unique constraint from VerificationCode.code
        # (validation is now handled at the application level per-user)
        migrations.AlterField(
            model_name='verificationcode',
            name='code',
            field=models.CharField(max_length=6),
        ),
    ]
