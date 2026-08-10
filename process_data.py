import csv

with open("data/daily_sales_data_0.csv", "r") as f1, \
     open("data/daily_sales_data_1.csv", "r") as f2, \
     open("data/daily_sales_data_2.csv", "r") as f3, \
     open("data/formatted_output.csv", "w", newline='') as out:

    writer = csv.DictWriter(out, ['Sales', 'Date', 'Region'])
    writer.writeheader()
    
    for reader in [csv.DictReader(f1), csv.DictReader(f2), csv.DictReader(f3)]:
        for row in reader:
            if row['product'] == 'Pink Morsel':
                sales = float(row['price'].replace('$', '')) * int(row['quantity'])
                writer.writerow({'Sales': f"${sales:.2f}", 
                               'Date': row['date'], 
                               'Region': row['region']})