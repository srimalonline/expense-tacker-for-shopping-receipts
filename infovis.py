import os
import pandas as pd
import matplotlib.pyplot as plt

def parse_receipt_file(file_path):
    """
    Parse a single receipt text file and extract item data into a list of dictionaries.
    """
    items = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.strip()
            # Ignore lines that are not relevant item data
            if line and not any(keyword in line.lower() for keyword in ['subtotal', 'cash', 'change', 'receipt', 'thank', 'invoice', 'city', 'tel', 'index', 'cashier', 'bill', 'table', 'tax']):
                # Split line by spaces to separate item, quantity, and price
                parts = line.split()
                if len(parts) >= 3 and parts[-2].isdigit() and is_float(parts[-1]):
                    # Extract the item name, quantity, and price
                    item_name = ' '.join(parts[:-2])
                    quantity = int(parts[-2])
                    price = float(parts[-1])

                    # Append to items list
                    items.append({
                        'Item': item_name,
                        'Quantity': quantity,
                        'Price': price
                    })

    return items

def is_float(value):
    """
    Check if a value can be converted to a float.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def merge_receipt_files(output_directory):
    """
    Merge all receipt files in the output directory into a single DataFrame.
    """
    all_items = []

    # Iterate over all files in the output directory
    for filename in os.listdir(output_directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(output_directory, filename)
            items = parse_receipt_file(file_path)
            all_items.extend(items)

    # Create a DataFrame from the list of all items
    df = pd.DataFrame(all_items)
    return df


def save_dataframe_to_csv(df, output_directory):
    """
    Save the merged DataFrame to a CSV file.
    """
    csv_path = os.path.join(output_directory, 'merged_receipts.csv')
    df.to_csv(csv_path, index=False)
    print(f"DataFrame saved to {csv_path}")


def visualize_total_quantity(df):
    """
    Visualize total quantity Bought per item using a bar chart.
    """
    # Group by Item and sum the quantities
    item_summary = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False)

    # Plot a bar chart for item quantities
    plt.figure(figsize=(10, 6))
    item_summary.plot(kind='bar', color='skyblue')
    plt.title('Total Quantity Bought per Item')
    plt.xlabel('Items')
    plt.ylabel('Total Quantity Bought')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def visualize_total_amount(df):
    """
    Visualize total sales amount per item using a horizontal bar chart.
    """
    # Group by Item and sum the total amounts (Price * Quantity)
    df['Total'] = df['Quantity'] * df['Price']
    amount_summary = df.groupby('Item')['Total'].sum().sort_values(ascending=True)  # Sort ascending for horizontal bar chart

    # Plot a horizontal bar chart for total amounts
    plt.figure(figsize=(10, 8))
    amount_summary.plot(kind='barh', color='coral')
    plt.title('Total Expense Amount per Item')
    plt.xlabel('Total Expense Amount')
    plt.ylabel('Items')
    plt.tight_layout()
    plt.show()


def visualize_top_items(df, top_n=5):
    """
    Visualize top N items by quantity bought using a pie chart.
    """
    # Group by Item and sum the quantities
    item_summary = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(top_n)

    # Plot a pie chart for top N items
    plt.figure(figsize=(8, 8))
    item_summary.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Set3')
    plt.title(f'Top {top_n} Items by Quantity Bought')
    plt.ylabel('')
    plt.tight_layout()
    plt.show()


def main():
    output_directory = 'output'

    # Merge all receipt files into a single DataFrame
    df = merge_receipt_files(output_directory)

    # Save the DataFrame to a CSV file
    save_dataframe_to_csv(df, output_directory)

    # Visualize the data
    visualize_total_quantity(df)
    visualize_total_amount(df)
    visualize_top_items(df, top_n=5)  # You can change the number of top items to visualize here


if __name__ == "__main__":
    main()
