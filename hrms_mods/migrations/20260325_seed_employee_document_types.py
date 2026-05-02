from hrms_mods.hrms_mods.utils.seed_employee_document_types import (
	seed_employee_document_types,
)


def execute():
	# Delegate to the same idempotent seeding logic used by `after_migrate`.
	seed_employee_document_types()

