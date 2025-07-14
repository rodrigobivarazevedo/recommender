#!/usr/bin/env python3
"""
HealthCast - FastAPI Startup Script
Simple script to run the health podcast recommendation system
"""

import uvicorn
import os
import sys

def main():
    """Main function to start the FastAPI application"""
    
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("Error: main.py not found. Please run this script from the app directory.")
        sys.exit(1)
    
    # Configuration
    host = "0.0.0.0"
    port = 8000
    reload = True
    
    print("🚀 Starting HealthCast - AI-Powered Health Podcast Recommendation System")
    print(f"📍 Server will be available at: http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print("🔄 Auto-reload enabled for development")
    print("=" * 60)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down HealthCast...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 