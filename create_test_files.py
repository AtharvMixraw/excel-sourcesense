"""
Script to create comprehensive Excel test files for SourceSense testing.
Run this to generate various Excel files with different data patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

def create_test_files():
    """Create various Excel files for testing different scenarios."""
    
    # Ensure uploads directory exists
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # 1. Create Company Employee Data (Multi-sheet workbook)
    print("📊 Creating company_employees.xlsx...")
    create_company_data(uploads_dir)
    
    # 2. Create Sales Analytics Data
    print("💰 Creating sales_analytics.xlsx...")
    create_sales_data(uploads_dir)
    
    # 3. Create Customer Survey Data (with data quality issues)
    print("📋 Creating customer_survey.xlsx...")
    create_survey_data(uploads_dir)
    
    # 4. Create Financial Report (complex data types)
    print("💹 Creating financial_report.xlsx...")
    create_financial_data(uploads_dir)
    
    # 5. Create Simple CSV for basic testing
    print("📄 Creating simple_products.csv...")
    create_csv_data(uploads_dir)
    
    print("\n✅ All test files created successfully!")
    print("📁 Files location: ./uploads/")
    print("\n🔬 Test Files Summary:")
    print("├── company_employees.xlsx    (Multi-sheet: Employees, Departments, Projects)")
    print("├── sales_analytics.xlsx      (Large dataset with date trends)")
    print("├── customer_survey.xlsx      (Data quality issues: nulls, duplicates)")
    print("├── financial_report.xlsx     (Complex: numbers, dates, categories)")
    print("└── simple_products.csv       (Basic CSV format)")

def create_company_data(output_dir):
    """Create company employee data with multiple sheets."""
    
    # Generate employee data
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Berlin']
    
    employees = []
    for i in range(1, 101):
        emp = {
            'employee_id': f'EMP{i:04d}',
            'first_name': f'FirstName{i}',
            'last_name': f'LastName{i}',
            'email': f'employee{i}@company.com',
            'department': random.choice(departments),
            'position': random.choice(['Junior', 'Senior', 'Lead', 'Manager', 'Director']),
            'salary': random.randint(40000, 150000),
            'hire_date': datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460)),
            'location': random.choice(locations),
            'is_active': random.choice([True, True, True, False]),  # 75% active
            'performance_rating': round(random.uniform(2.0, 5.0), 1),
            'bonus_eligible': random.choice([True, False]),
        }
        employees.append(emp)
    
    employees_df = pd.DataFrame(employees)
    
    # Generate department data
    dept_data = []
    for dept in departments:
        dept_info = {
            'department_name': dept,
            'department_head': f'{dept} Manager',
            'budget': random.randint(500000, 2000000),
            'employee_count': len(employees_df[employees_df['department'] == dept]),
            'established_date': datetime(2015, 1, 1) + timedelta(days=random.randint(0, 2000)),
            'cost_center': f'CC{random.randint(1000, 9999)}'
        }
        dept_data.append(dept_info)
    
    departments_df = pd.DataFrame(dept_data)
    
    # Generate project data
    projects = []
    project_names = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta']
    statuses = ['Planning', 'In Progress', 'Testing', 'Completed', 'On Hold']
    
    for i, project_name in enumerate(project_names):
        project = {
            'project_id': f'PRJ{i+1:03d}',
            'project_name': f'Project {project_name}',
            'project_manager': random.choice(employees_df['employee_id'].tolist()),
            'department': random.choice(departments),
            'start_date': datetime(2023, 1, 1) + timedelta(days=random.randint(0, 300)),
            'end_date': datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365)),
            'budget': random.randint(50000, 500000),
            'status': random.choice(statuses),
            'priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'completion_percentage': random.randint(0, 100)
        }
        projects.append(project)
    
    projects_df = pd.DataFrame(projects)
    
    # Save to Excel with multiple sheets
    with pd.ExcelWriter(output_dir / 'company_employees.xlsx', engine='openpyxl') as writer:
        employees_df.to_excel(writer, sheet_name='Employees', index=False)
        departments_df.to_excel(writer, sheet_name='Departments', index=False)
        projects_df.to_excel(writer, sheet_name='Projects', index=False)

def create_sales_data(output_dir):
    """Create sales analytics data with time series and geographic info."""
    
    # Generate daily sales data for 2 years
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    products = ['Widget A', 'Widget B', 'Gadget X', 'Gadget Y', 'Tool Pro', 'Tool Lite']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa']
    sales_reps = [f'Rep_{i:02d}' for i in range(1, 21)]
    
    sales_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Generate 5-15 sales records per day
        daily_records = random.randint(5, 15)
        
        for _ in range(daily_records):
            # Seasonal trends
            month = current_date.month
            seasonal_multiplier = 1.0
            if month in [11, 12]:  # Holiday season
                seasonal_multiplier = 1.5
            elif month in [6, 7, 8]:  # Summer
                seasonal_multiplier = 1.2
            
            base_amount = random.uniform(100, 5000)
            
            sale = {
                'date': current_date,
                'product': random.choice(products),
                'region': random.choice(regions),
                'sales_rep': random.choice(sales_reps),
                'quantity': random.randint(1, 50),
                'unit_price': round(random.uniform(10, 500), 2),
                'total_amount': round(base_amount * seasonal_multiplier, 2),
                'discount_percent': round(random.uniform(0, 25), 1),
                'customer_type': random.choice(['New', 'Existing', 'VIP']),
                'payment_method': random.choice(['Credit Card', 'Bank Transfer', 'PayPal', 'Cash']),
                'order_priority': random.choice(['Standard', 'Express', 'Urgent']),
                'shipping_cost': round(random.uniform(5, 50), 2)
            }
            sales_data.append(sale)
        
        current_date += timedelta(days=1)
    
    sales_df = pd.DataFrame(sales_data)
    
    # Add calculated columns
    sales_df['profit_margin'] = sales_df['total_amount'] * random.uniform(0.1, 0.4)
    sales_df['net_amount'] = sales_df['total_amount'] - (sales_df['total_amount'] * sales_df['discount_percent'] / 100)
    
    sales_df.to_excel(output_dir / 'sales_analytics.xlsx', index=False)

def create_survey_data(output_dir):
    """Create customer survey data with intentional data quality issues."""
    
    # This file will have various data quality issues to test the app's handling
    survey_responses = []
    
    for i in range(1, 501):
        # Introduce some data quality issues intentionally
        response = {
            'response_id': i,
            'customer_id': f'CUST{i:04d}' if i % 10 != 0 else None,  # 10% missing customer IDs
            'survey_date': datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300)),
            'age': random.randint(18, 80) if i % 15 != 0 else None,  # Some missing ages
            'gender': random.choice(['Male', 'Female', 'Other', 'Prefer not to say']) if i % 20 != 0 else None,
            'satisfaction_score': random.randint(1, 10),
            'product_rating': random.randint(1, 5) if i % 8 != 0 else None,  # Some missing ratings
            'recommend_likelihood': random.randint(0, 10),
            'annual_income': random.randint(20000, 200000) if i % 12 != 0 else None,
            'education_level': random.choice(['High School', 'Bachelor', 'Master', 'PhD', 'Other']),
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']) if i % 25 != 0 else None,
            'feedback_text': f'This is feedback from customer {i}' if i % 30 != 0 else None,
            'contact_email': f'customer{i}@email.com' if random.random() > 0.1 else 'invalid-email',  # Some invalid emails
        }
        
        # Introduce some duplicate records (data quality issue)
        survey_responses.append(response)
        if i % 50 == 0:  # 2% duplicates
            survey_responses.append(response.copy())
    
    survey_df = pd.DataFrame(survey_responses)
    survey_df.to_excel(output_dir / 'customer_survey.xlsx', index=False)

def create_financial_data(output_dir):
    """Create financial report with complex data types and calculations."""
    
    # Monthly financial data
    months = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')
    
    financial_data = []
    
    for month in months:
        record = {
            'reporting_month': month,
            'revenue': round(random.uniform(500000, 2000000), 2),
            'cost_of_goods_sold': round(random.uniform(200000, 800000), 2),
            'operating_expenses': round(random.uniform(150000, 500000), 2),
            'marketing_spend': round(random.uniform(50000, 200000), 2),
            'research_development': round(random.uniform(30000, 150000), 2),
            'tax_rate': round(random.uniform(0.15, 0.35), 3),
            'employee_count': random.randint(80, 120),
            'currency': 'USD',
            'exchange_rate_eur': round(random.uniform(0.8, 0.9), 4),
            'exchange_rate_gbp': round(random.uniform(0.7, 0.8), 4),
            'market_segment': random.choice(['Enterprise', 'SMB', 'Consumer']),
            'quarter': f'Q{((month.month-1)//3)+1}',
            'fiscal_year': month.year,
            'is_audited': random.choice([True, False]),
            'notes': f'Financial data for {month.strftime("%B %Y")}'
        }
        
        # Calculate derived fields
        record['gross_profit'] = record['revenue'] - record['cost_of_goods_sold']
        record['ebitda'] = record['gross_profit'] - record['operating_expenses']
        record['net_income'] = record['ebitda'] * (1 - record['tax_rate'])
        record['profit_margin'] = round((record['net_income'] / record['revenue']) * 100, 2)
        
        financial_data.append(record)
    
    financial_df = pd.DataFrame(financial_data)
    financial_df.to_excel(output_dir / 'financial_report.xlsx', index=False)

def create_csv_data(output_dir):
    """Create a simple CSV file for basic testing."""
    
    products = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys']
    
    for i in range(1, 51):
        product = {
            'product_id': f'PROD{i:03d}',
            'product_name': f'Product {i}',
            'category': random.choice(categories),
            'price': round(random.uniform(9.99, 999.99), 2),
            'stock_quantity': random.randint(0, 500),
            'supplier_id': f'SUP{random.randint(1, 10):02d}',
            'is_active': random.choice([True, False]),
            'launch_date': datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1400)),
            'weight_kg': round(random.uniform(0.1, 50.0), 2),
            'rating': round(random.uniform(1.0, 5.0), 1),
            'description': f'High-quality {random.choice(categories).lower()} product'
        }
        products.append(product)
    
    products_df = pd.DataFrame(products)
    products_df.to_csv(output_dir / 'simple_products.csv', index=False)

if __name__ == "__main__":
    print("🚀 Creating comprehensive Excel test files for SourceSense...")
    print("=" * 60)
    
    create_test_files()
    
    print("\n" + "=" * 60)
    print("🎯 Testing Recommendations:")
    print("\n1. 📊 company_employees.xlsx - Test multi-sheet processing")
    print("2. 💰 sales_analytics.xlsx - Test large dataset (5000+ rows)")
    print("3. 📋 customer_survey.xlsx - Test data quality detection")
    print("4. 💹 financial_report.xlsx - Test complex data types")
    print("5. 📄 simple_products.csv - Test basic CSV functionality")
    
    print("\n🔍 What to Look For:")
    print("• Metadata extraction accuracy")
    print("• Data type detection")
    print("• Data quality metrics (nulls, duplicates)")
    print("• Visualization generation")
    print("• Performance with different file sizes")
    
    print("\n✨ Ready for testing! Upload these files to your SourceSense app.")
