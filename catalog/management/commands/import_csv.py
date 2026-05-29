"""
Django management command to import IS elements from a CSV file.

Place this file at:
    yourapp/management/commands/import_csv.py

Make sure yourapp/management/__init__.py and
yourapp/management/commands/__init__.py both exist (can be empty).

Usage:
    python manage.py import_csv path/to/data.csv
"""

import csv
import re

from django.core.management.base import BaseCommand, CommandError

from catalog.models import (
    Accession, Family, Group, ISElement, ORF, Origin, Synonym
)


def parse_ir(value):
    """
    Parse Inverted Repeat field into (ir_min, ir_max).
    '18'    → (18, None)
    '17/18' → (17, 18)
    """
    value = value.strip()
    # Catch empty strings or NA before trying to convert
    value = value.replace('?', '').replace('~', '').replace('bp', '').replace('BP', '').strip()
    if value.upper() == 'NA' or value == '' or value == "N":
        return None, None  # Or return 0, 0 if your database doesn't allow NULLs
    if '/' in value:
        parts = value.split('/')
        return int(parts[0]), int(parts[1])
    elif '-' in value:
        parts = value.split('-')
        return int(parts[0]), int(parts[1])
    return parse_int(value), None


def parse_orfs(value):
    """
    Parse ORF field into a list of (aa_length, start, end) tuples.
    '384 (87-1241)'                      → [(384, 87, 1241)]
    '122 (84-452)146 (404-844)253(84-844)' → [(122, 84, 452), (146, 404, 844), (253, 84, 844)]
    """
    pattern = r'(\d+)\s*\((\d+)-(\d+)\)'
    return [
        (int(aa), int(start), int(end))
        for aa, start, end in re.findall(pattern, value)
    ]

def parse_int(value):
    """Safely convert strings to integers, catching various 'empty' text values."""
    value = value.strip()
    value = value.replace('?', '').replace('~', '').strip()
    # Check against a list of possible empty values
    value = value.replace('?', '').replace('~', '').replace('bp', '').replace('BP', '').strip()
    if value.upper() in ['NA', 'NONE', 'NULL', '']:
        return None
    return int(value)

def parse_synonyms(value):
    """
    Parse Synonyms field into a list of strings.
    Assumes comma-separated — adjust delimiter if needed.
    'ISAcma1,ISAcma3' → ['ISAcma1', 'ISAcma3']
    """
    return [s.strip() for s in value.split(',') if s.strip()]


class Command(BaseCommand):
    help = 'Import IS elements from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='Skip rows with errors instead of stopping'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        skip_errors = options['skip_errors']

        try:
            csv_file = open(csv_path, newline='', encoding='utf-8')
        except FileNotFoundError:
            raise CommandError(f'File not found: {csv_path}')

        reader = csv.DictReader(csv_file)

        created_count = 0
        skipped_count = 0

        with csv_file:
            for row_num, row in enumerate(reader, start=2):  # start=2 accounts for header row
                try:
                    # ----------------------------------------------------------------
                    # 1. Get or create lookup models
                    # ----------------------------------------------------------------
                    family, _ = Family.objects.get_or_create(
                        name=row['Family'].strip()
                    )

                    raw_group = row['Group'].strip()
                    if raw_group and raw_group.upper() != 'NA':
                        group, _ = Group.objects.get_or_create(
                            name=raw_group,
                            defaults={'family': family}
                        )
                    else:
                        group = None

                    origin, _ = Origin.objects.get_or_create(
                        name=row['Origin'].strip()
                    )

                    accession, _ = Accession.objects.get_or_create(
                        number=row['Accession Number'].strip()
                    )

                    # ----------------------------------------------------------------
                    # 2. Parse scalar fields
                    # ----------------------------------------------------------------
                    ir_min, ir_max = parse_ir(row['IR'].strip())

                    # ----------------------------------------------------------------
                    # 3. Create ISElement (skip if name already exists)
                    # ----------------------------------------------------------------
                    is_element, created = ISElement.objects.get_or_create(
                        name=row['Name'].strip(),
                        defaults={
                            'number':    parse_int(row['N°'].strip()),
                            'family':    family,
                            'group':     group,
                            'origin':    origin,
                            'accession': accession,
                            'iso':       row['Iso'].strip(),
                            'length':    parse_int(row['Length'].strip()),
                            'ir_min':    ir_min,
                            'ir_max':    ir_max,
                            'dr':        parse_int(row['DR'].strip()),
                            'url':       row['url'].strip(),
                        }
                    )

                    if not created:
                        self.stdout.write(
                            self.style.WARNING(f'Row {row_num}: {is_element.name} already exists, skipping')
                        )
                        skipped_count += 1
                        continue

                    # ----------------------------------------------------------------
                    # 4. Create Synonyms
                    # ----------------------------------------------------------------
                    for syn_name in parse_synonyms(row['Synonyms']):
                        Synonym.objects.get_or_create(
                            name=syn_name,
                            is_element=is_element
                        )

                    # ----------------------------------------------------------------
                    # 5. Create ORFs
                    # ----------------------------------------------------------------
                    for aa_length, start, end in parse_orfs(row['ORF']):
                        ORF.objects.create(
                            is_element=is_element,
                            aa_length=aa_length,
                            start=start,
                            end=end
                        )

                    created_count += 1
                    self.stdout.write(f'Row {row_num}: imported {is_element.name}')

                except Exception as e:
                    if skip_errors:
                        self.stdout.write(
                            self.style.ERROR(f'Row {row_num}: skipped due to error — {e}')
                        )
                        skipped_count += 1
                    else:
                        raise CommandError(f'Row {row_num}: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — {created_count} imported, {skipped_count} skipped'
        ))
