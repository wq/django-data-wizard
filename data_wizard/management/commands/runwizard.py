from django.core.management.base import BaseCommand, CommandError
from ...models import Run
from django.contrib.contenttypes.models import ContentType
from ...serializers import ContentTypeIdField
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
import getpass


User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("contenttype_id")
        parser.add_argument("object_id")
        parser.add_argument("--serializer")
        parser.add_argument("--loader")
        parser.add_argument("--username")
        parser.add_argument("--quiet", action="store_true")

    def handle(self, *args, **options):
        ctid = options["contenttype_id"]

        try:
            ct = ContentTypeIdField(
                queryset=ContentType.objects.all()
            ).to_internal_value(ctid)
        except ValidationError as e:
            raise CommandError(e)

        objid = options["object_id"]
        try:
            ct.get_object_for_this_type(pk=objid)
        except ct.model_class().DoesNotExist:
            raise CommandError(
                "Could not find {} with pk={}".format(ct, objid)
            )

        username = options["username"] or getpass.getuser()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
        except User.DoesNotExist:
            raise CommandError("No such user '{}'".format(username))

        run = Run.objects.create(
            user=user,
            content_type=ct,
            object_id=objid,
            serializer=options["serializer"],
            loader=options["loader"],
        )

        if not run.serializer:
            raise CommandError("No serializer specified.")

        try:
            result = run.run_task(
                "data_wizard.tasks.auto_import",
                use_async=False,
            )
        except Exception as e:
            raise CommandError(e)

        if "error" in result:
            raise CommandError(result["error"])
        elif "result" in result:
            result = result["result"]

        if "action" in result:
            # TODO: Interactive CLI for resolving input?
            raise CommandError(
                "{message} for {unknown_count} {action}".format(
                    message=result.get("message", "Input Needed"),
                    unknown_count=result.get("unknown_count", "?"),
                    action=result["action"],
                )
            )

        if not options["quiet"]:
            self.stdout.write(
                "{total} row imported ({skipped} skipped).".format(
                    total=result["total"],
                    skipped=len(result["skipped"]),
                )
            )
