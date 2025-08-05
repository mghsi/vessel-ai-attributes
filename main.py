import os
from app.app_factory import create_app

def main():
    """Main entry point for the application"""
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Boat Analyzer API on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
