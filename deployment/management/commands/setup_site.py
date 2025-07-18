from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup the Django site configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost:5000',
            help='Domain name for the site (e.g., csciauto1.etsu.edu:5000)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Static Site Deployment Server',
            help='Name for the site'
        )
    
    def handle(self, *args, **options):
        domain = options['domain']
        name = options['name']
        
        # Update or create the site
        site, created = Site.objects.get_or_create(id=1)
        site.domain = domain
        site.name = name
        site.save()
        
        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f'{action} site: {name} at {domain}')
        )
        
        # Display current configuration
        self.stdout.write(f"\nCurrent site configuration:")
        self.stdout.write(f"  Domain: {site.domain}")
        self.stdout.write(f"  Name: {site.name}")
        self.stdout.write(f"  ID: {site.id}")
        
        # Show sample URLs
        protocol = 'https'  # Assume HTTPS
        base_url = f"{protocol}://{domain}"
        
        self.stdout.write(f"\nSample URLs:")
        self.stdout.write(f"  Admin: {base_url}/admin/")
        self.stdout.write(f"  Dashboard: {base_url}/")
        self.stdout.write(f"  User sites: {base_url}/username/")
