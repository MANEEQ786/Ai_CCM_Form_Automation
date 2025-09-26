import os
import sys
from django.core.management import execute_from_command_line
 
def runserver():
    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
 
    # Check if STATIC_IP and STATIC_PORT are defined in settings
    from django.conf import settings
    if not hasattr(settings, 'STATIC_IP') or not hasattr(settings, 'STATIC_PORT'):
        raise ValueError("STATIC_IP and STATIC_PORT must be defined in settings.py")
 
    # Get the static IP and port from settings
    static_ip = settings.STATIC_IP
    static_port = settings.STATIC_PORT
 
    # Update sys.argv to include the desired IP and port
    sys.argv = [
        sys.argv[0],
        'runserver',
        f"{static_ip}:{static_port}",
    ]
 
    # Execute the runserver command
    execute_from_command_line(sys.argv)
 
if __name__ == "__main__":
    runserver()