"""
Simple test script for Excel metadata extraction
"""
import asyncio
import pandas as pd
from pathlib import Path

async def test_excel_client():
    # Create a simple test Excel file
    test_data = {
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Salary': [50000, 60000, 75000, 55000, 68000]
    }
    
    df = pd.DataFrame(test_data)
    test_file = Path('./test_file.xlsx')
    df.to_excel(test_file, index=False)
    
    print(f"Created test file: {test_file}")
    
    # Test the Excel client
    from app.clients import ExcelClient
    
    client = ExcelClient({'file_path': str(test_file)})
    success = await client.connect()
    
    if success:
        print("✅ Excel client connected successfully!")
        print(f"Sheets: {client.get_sheet_names()}")
        print(f"File metadata: {client.get_file_metadata()}")
        
        # Test data extraction
        sheet_data = client.get_sheet_data('Sheet1')
        if sheet_data is not None:
            print(f"✅ Data extracted: {len(sheet_data)} rows, {len(sheet_data.columns)} columns")
        
        await client.disconnect()
    else:
        print("❌ Failed to connect to Excel file")

if __name__ == "__main__":
    asyncio.run(test_excel_client())
