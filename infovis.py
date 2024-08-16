import os
import csv

def summarize_logs():
    log_dir = 'logs'
    summaries = []

    if not os.path.exists(log_dir):
        print(f"No logs found in {log_dir}.")
        return

    # Aggregate all logs
    for log_file in os.listdir(log_dir):
        if log_file.endswith('.csv'):
            with open(os.path.join(log_dir, log_file), mode='r') as file:
                reader = csv.reader(file)
                items = []
                subtotal, cash, change = None, None, None

                for row in reader:
                    if row[0] == 'Subtotal':
                        subtotal = row[1]
                    elif row[0] == 'Cash':
                        cash = row[1]
                    elif row[0] == 'Change':
                        change = row[1]
                    else:
                        items.append(row)

                summaries.append({
                    'file': log_file,
                    'items': items,
                    'subtotal': subtotal,
                    'cash': cash,
                    'change': change
                })

    # Print out the summaries
    for summary in summaries:
        print(f"\nSummary for {summary['file']}:")
        print("Items:")
        for item in summary['items']:
            print(f"  {item[0]} - Quantity: {item[1]}, Total: {item[2]}")
        print(f"Subtotal: {summary['subtotal']}")
        print(f"Cash: {summary['cash']}")
        print(f"Change: {summary['change']}")

if __name__ == "__main__":
    summarize_logs()
