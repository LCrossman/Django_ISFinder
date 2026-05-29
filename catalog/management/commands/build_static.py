import os
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from catalog.views import index, elements_by_origin
from catalog.models import Origin

class Command(BaseCommand):
    help = 'Freezes the Django database into static HTML files for GitHub Pages'

    def handle(self, *args, **kwargs):
        # 1. Create the output folder (where GitHub Pages will read from)
        out_dir = os.path.join(os.getcwd(), 'static_build')
        os.makedirs(out_dir, exist_ok=True)
        
        # We need a fake request generator to trigger our views
        factory = RequestFactory()

        # 2. Build the main Index page
        self.stdout.write("Building index.html...")
        request = factory.get('/')
        response = index(request)
        
        with open(os.path.join(out_dir, 'index.html'), 'wb') as f:
            f.write(response.content)

        # 3. Build the Origin pages
        origin_dir = os.path.join(out_dir, 'origin')
        os.makedirs(origin_dir, exist_ok=True)

        for origin in Origin.objects.all():
            self.stdout.write(f"Building page for {origin.name}...")
            
            # Create the fake request
            request = factory.get(f'/origin/{origin.name}/')
            response = elements_by_origin(request, origin_name=origin.name)

            # GitHub Pages doesn't like spaces in URLs, so replace them with underscores
            safe_filename = origin.name.replace(' ', '_') + '.html'
            file_path = os.path.join(origin_dir, safe_filename)

            with open(file_path, 'wb') as f:
                f.write(response.content)

        self.stdout.write(self.style.SUCCESS(f'Successfully built static site in: {out_dir}'))
