import pandas as pd
import xlsxwriter

#Pushes dataframe to new excel document in current directory
def data_frame_to_excel(df,excel_name="output.xlsx",sheet_name ="Sheet1", table_name="Table1", table_style="Table Style Medium 2"):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(excel_name, engine="xlsxwriter")

    # Write the dataframe data to XlsxWriter.
    df.to_excel(writer, sheet_name=sheet_name, startrow=1,header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{"header": column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col-1, {"name":table_name,"columns": column_settings,"style": table_style})

    # Make the columns wider for clarity.
    #worksheet.set_column(0, max_col - 1, 12)
    worksheet.autofit()
    # Close the Pandas Excel writer and output the Excel file.
    writer.close()