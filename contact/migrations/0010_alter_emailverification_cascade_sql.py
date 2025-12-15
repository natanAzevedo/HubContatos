from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0009_alter_contact_owner_on_delete'),
    ]

    operations = [
        # Alterar constraint EmailVerification.user para ON DELETE CASCADE
        migrations.RunSQL(
            sql="""
            ALTER TABLE contact_emailverification 
            DROP CONSTRAINT contact_emailverification_user_id_308c14af_fk_auth_user_id;
            
            ALTER TABLE contact_emailverification
            ADD CONSTRAINT contact_emailverification_user_id_308c14af_fk_auth_user_id
            FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE contact_emailverification 
            DROP CONSTRAINT contact_emailverification_user_id_308c14af_fk_auth_user_id;
            
            ALTER TABLE contact_emailverification
            ADD CONSTRAINT contact_emailverification_user_id_308c14af_fk_auth_user_id
            FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;
            """
        ),
        # Alterar constraint Profile.user para ON DELETE CASCADE
        migrations.RunSQL(
            sql="""
            ALTER TABLE contact_profile 
            DROP CONSTRAINT contact_profile_user_id_key;
            
            ALTER TABLE contact_profile
            DROP CONSTRAINT IF EXISTS contact_profile_user_id_fk;
            
            ALTER TABLE contact_profile
            ADD CONSTRAINT contact_profile_user_id_fk
            FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE contact_profile 
            DROP CONSTRAINT IF EXISTS contact_profile_user_id_fk;
            """
        ),
        # Alterar constraint Contact.owner para ON DELETE CASCADE
        migrations.RunSQL(
            sql="""
            ALTER TABLE contact_contact 
            DROP CONSTRAINT IF EXISTS contact_contact_owner_id_fk;
            
            ALTER TABLE contact_contact
            ADD CONSTRAINT contact_contact_owner_id_fk
            FOREIGN KEY (owner_id) REFERENCES auth_user(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            ALTER TABLE contact_contact 
            DROP CONSTRAINT IF EXISTS contact_contact_owner_id_fk;
            """
        ),
    ]
