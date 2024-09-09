import os
import pandas as pd
import plotly.express as px


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
            if line and not any(keyword in line.lower() for keyword in
                                ['subtotal', 'cash', 'change', 'receipt', 'thank', 'invoice', 'city', 'tel', 'index',
                                 'cashier', 'bill', 'table', 'tax']):
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
    Visualize total quantity sold per item using an interactive bar chart with Plotly.
    """
    # Group by Item and sum the quantities
    item_summary = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).reset_index()

    # Create an interactive bar chart
    fig = px.bar(item_summary, x='Item', y='Quantity', title='Total Quantity Sold per Item',
                 labels={'Quantity': 'Total Quantity Sold', 'Item': 'Items'},
                 color='Quantity', color_continuous_scale='Blues')

    # Show the plot
    fig.show()


def visualize_total_amount(df):
    """
    Visualize total sales amount per item using an interactive horizontal bar chart with Plotly.
    """
    # Group by Item and sum the total amounts (Price * Quantity)
    df['Total'] = df['Quantity'] * df['Price']
    amount_summary = df.groupby('Item')['Total'].sum().sort_values(ascending=False).reset_index()

    # Create an interactive horizontal bar chart
    fig = px.bar(amount_summary, x='Total', y='Item', orientation='h',
                 title='Total Sales Amount per Item',
                 labels={'Total': 'Total Sales Amount', 'Item': 'Items'},
                 color='Total', color_continuous_scale='Sunset')

    # Show the plot
    fig.show()


def visualize_top_items(df, top_n=5):
    """
    Visualize top N items by quantity sold using an interactive pie chart with Plotly.
    """
    # Group by Item and sum the quantities
    item_summary = df.groupby('Item')['Quantity'].sum().sort_values(ascending=False).head(top_n).reset_index()

    # Create an interactive pie chart
    fig = px.pie(item_summary, values='Quantity', names='Item',
                 title=f'Top {top_n} Items by Quantity Sold',
                 color_discrete_sequence=px.colors.qualitative.Set3)

    # Show the plot
    fig.show()


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
