#!/usr/bin/env python3
"""
Create a test database with sample KML-ready data for CORE_Austere
"""
import sqlite3
import os
import json
from datetime import datetime

def create_test_database(db_path="test_reports.db"):
    """Create a test database with sample data"""
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Apply schema first
    print("Applying schema...")
    os.system(f'python apply_schema.py --db "{db_path}"')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Sample data with MGRS coordinates
    sample_reports = [
        {
            "id": "report_001",
            "file_hash": "abc123def456",
            "highest_classification": "UNCLASSIFIED",
            "caveats": "",
            "file_path": "/test/report1.pdf",
            "locations": "Baghdad|Iraq",
            "timeframes": "2023-01-15|2023-01-20",
            "subjects": "Infrastructure Assessment",
            "topics": "Transportation|Security",
            "keywords": "bridge inspection security checkpoint",
            "MGRS": "38SMB4484536781",  # Baghdad area
            "images": None,
            "full_text": "This report covers the infrastructure assessment of key transportation routes in Baghdad, focusing on bridge conditions and security checkpoints.",
            "processed_time": datetime.now().isoformat()
        },
        {
            "id": "report_002", 
            "file_hash": "def456ghi789",
            "highest_classification": "UNCLASSIFIED",
            "caveats": "",
            "file_path": "/test/report2.pdf",
            "locations": "Kabul|Afghanistan",
            "timeframes": "2023-02-01|2023-02-05",
            "subjects": "Market Analysis",
            "topics": "Economy|Population",
            "keywords": "market vendors economy trade",
            "MGRS": "42SXD8914734521",  # Kabul area
            "images": None,
            "full_text": "Economic analysis of local markets in Kabul, including vendor interviews and trade pattern observations.",
            "processed_time": datetime.now().isoformat()
        },
        {
            "id": "report_003",
            "file_hash": "ghi789jkl012", 
            "highest_classification": "UNCLASSIFIED",
            "caveats": "",
            "file_path": "/test/report3.pdf",
            "locations": "Damascus|Syria",
            "timeframes": "2023-03-10|2023-03-15", 
            "subjects": "Urban Development",
            "topics": "Infrastructure|Construction",
            "keywords": "construction buildings urban development",
            "MGRS": "37SCT7654321098",  # Damascus area
            "images": None,
            "full_text": "Survey of urban development projects in Damascus, documenting new construction and infrastructure improvements.",
            "processed_time": datetime.now().isoformat()
        }
    ]
    
    # Insert sample data
    print("Inserting sample data...")
    for report in sample_reports:
        cursor.execute("""
            INSERT INTO reports (
                id, file_hash, highest_classification, caveats, file_path,
                locations, timeframes, subjects, topics, keywords, MGRS,
                images, full_text, processed_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report["id"], report["file_hash"], report["highest_classification"],
            report["caveats"], report["file_path"], report["locations"],
            report["timeframes"], report["subjects"], report["topics"],
            report["keywords"], report["MGRS"], report["images"],
            report["full_text"], report["processed_time"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Test database created: {db_path}")
    print(f"   - {len(sample_reports)} sample reports with MGRS coordinates")
    print(f"   - Ready for search and KML export testing")
    print(f"\nTo test, run:")
    print(f'   python run_app.py --db "{db_path}"')
    
    return db_path

if __name__ == "__main__":
    create_test_database()
