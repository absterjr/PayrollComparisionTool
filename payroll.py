import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
# Create the main window
window = tk.Tk()
window.title('Payroll Comparison Tool')
window.geometry('550x650')


# Global variables to store the loaded datasets
df1 = None
df2 = None

# Function to load Dataset 1
def load_dataset1():
    global df1
    file_path = filedialog.askopenfilename(filetypes=(('Excel Files', ('*.xls', '*.xlsx')), ('CSV Files', '*.csv'), ('All Files', '*.*')))
    if file_path:
        try:
            if file_path.endswith('.csv'):
                df1 = pd.read_csv(file_path)
            else:
                df1 = pd.read_excel(file_path)
            messagebox.showinfo('Success', 'Dataset 1 loaded successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load Dataset 1:\n{str(e)}')

# Function to load Dataset 2
def load_dataset2():
    global df2
    file_path = filedialog.askopenfilename(filetypes=(('Excel Files', ('*.xls', '*.xlsx')), ('CSV Files', '*.csv'), ('All Files', '*.*')))
    if file_path:
        try:
            if file_path.endswith('.csv'):
                df2 = pd.read_csv(file_path)
            else:
                df2 = pd.read_excel(file_path)
            messagebox.showinfo('Success', 'Dataset 2 loaded successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load Dataset 2:\n{str(e)}')

            
def compare_basic_pay():
    global df1, df2

    if df1 is None or df2 is None:
        messagebox.showerror('Error', 'Please load both datasets first.')
        return

    # Function to calculate total basic pay for a row (including Basic Pay Adjustment)
    def calculate_total_basic_pay(row):
        return row['Basic Pay'] + row['Basic Pay Arrears'] + row.get('Basic Pay Adjustment', 0)

    # Calculate last month's total basic pay for each employee in df1
    last_month_total_basic_pay_dict = {}  # Dictionary to store last month's total basic pay for each employee
    for _, row in df1.iterrows():
        employee_id = row['Person No']
        last_month_total_basic_pay_dict[employee_id] = calculate_total_basic_pay(row)

    # Compare Basic Pay for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    filtered_data_executives.insert(1, 'Last Month Total Basic Pay', df2.loc[conditions_executives, 'Person No'].map(last_month_total_basic_pay_dict).fillna(0))
    filtered_data_executives.insert(2, 'Current Month Total Basic Pay', df2.loc[conditions_executives].apply(calculate_total_basic_pay, axis=1))
    filtered_data_executives.insert(3, 'Percentage Change', (filtered_data_executives['Current Month Total Basic Pay'] - filtered_data_executives['Last Month Total Basic Pay']) / filtered_data_executives['Last Month Total Basic Pay'] * 100)
    filtered_data_executives.insert(0, 'Condition', 'Basic Pay')

    # Compare Basic Pay for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    filtered_data_non_executives.insert(1, 'Last Month Total Basic Pay', df2.loc[conditions_non_executives, 'Person No'].map(last_month_total_basic_pay_dict).fillna(0))
    filtered_data_non_executives.insert(2, 'Current Month Total Basic Pay', df2.loc[conditions_non_executives].apply(calculate_total_basic_pay, axis=1))
    filtered_data_non_executives.insert(3, 'Percentage Change', (filtered_data_non_executives['Current Month Total Basic Pay'] - filtered_data_non_executives['Last Month Total Basic Pay']) / filtered_data_non_executives['Last Month Total Basic Pay'] * 100)
    filtered_data_non_executives.insert(0, 'Condition', 'Basic Pay')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')



def compare_hra():
    global df2

    if df2 is None:
        messagebox.showerror('Error', 'Please load the current payroll dataset first.')
        return

    # Prompt user for the threshold percentage
    threshold_percentage_hra = float(entry_threshold_hra.get()) / 100

    # Check if 'HRA Adjustment' column is present in df2
    if 'HRA Adjustment' in df2.columns:
        hra_adjustment_col = 'HRA Adjustment'
    else:
        # If 'HRA Adjustment' column is not present, fill it with 0
        df2['HRA Adjustment'] = 0
        hra_adjustment_col = 'HRA Adjustment'

    # Check if 'Basic Pay Adjustment' column is present in df2
    if 'Basic Pay Adjustment' in df2.columns:
        basic_pay_adjustment_col = 'Basic Pay Adjustment'
    else:
        # If 'Basic Pay Adjustment' column is not present, fill it with 0
        df2['Basic Pay Adjustment'] = 0
        basic_pay_adjustment_col = 'Basic Pay Adjustment'

    # Calculate the total basic pay with adjustment for each employee
    df2['Total Basic Pay'] = df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col]

    # Group data by Employee ID and calculate HRA Percentage for each employee
    df2['HRA Percentage'] = ((df2['House Rent Allowance'] + df2['House Rent Allow Arrears'] + df2[hra_adjustment_col]) / df2['Total Basic Pay']) * 100

    # Compare HRA for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    conditions_executives &= ((df2['HRA Percentage'] < (threshold_percentage_hra + 0.5)) & (df2['HRA Percentage'] > (threshold_percentage_hra - 0.5)))
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    filtered_data_executives.drop('HRA Percentage', axis=1, inplace=True)  # Drop the column if it exists
    filtered_data_executives.insert(1, 'HRA Percentage', df2.loc[conditions_executives, 'HRA Percentage'])
    filtered_data_executives.insert(0, 'Condition', 'HRA')

    # Compare HRA for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    conditions_non_executives &= ((df2['HRA Percentage'] < (threshold_percentage_hra + 0.5)) & (df2['HRA Percentage'] > (threshold_percentage_hra - 0.5)))
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    filtered_data_non_executives.drop('HRA Percentage', axis=1, inplace=True)  # Drop the column if it exists
    filtered_data_non_executives.insert(1, 'HRA Percentage', df2.loc[conditions_non_executives, 'HRA Percentage'])
    filtered_data_non_executives.insert(0, 'Condition', 'HRA')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')



def compare_da():
    global df2

    if df2 is None:
        messagebox.showerror('Error', 'Please load the current payroll dataset first.')
        return

    # Check if 'Basic Pay Adjustment' column is present in df2
    if 'Basic Pay Adjustment' in df2.columns:
        basic_pay_adjustment_col = 'Basic Pay Adjustment'
    else:
        # If 'Basic Pay Adjustment' column is not present, fill it with 0
        df2['Basic Pay Adjustment'] = 0
        basic_pay_adjustment_col = 'Basic Pay Adjustment'

    # Prompt user for the threshold percentage
    threshold_percentage_da = float(entry_threshold_da.get()) / 100

    # Compare DA for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    conditions_executives &= (df2['IDA'] + df2['IDA Adjustment'] + df2['IDA Arrears']) >= (1 - 0.005) * threshold_percentage_da * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    conditions_executives &= (df2['IDA'] + df2['IDA Adjustment'] + df2['IDA Arrears']) <= (1 + 0.005) * threshold_percentage_da * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    filtered_data_executives.insert(1, 'DA Percentage', (filtered_data_executives['IDA'] + filtered_data_executives['IDA Adjustment'] + filtered_data_executives['IDA Arrears']) / filtered_data_executives['Total Basic Pay'] * 100)
    filtered_data_executives.insert(0, 'Condition', 'DA')

    # Compare DA for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    conditions_non_executives &= (df2['SDA NEx'] + df2['SDA Arrears'] + df2['VDA NEx'] + df2['VDA Arrears']) >= (1 - 0.005) * threshold_percentage_da * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    conditions_non_executives &= (df2['SDA NEx'] + df2['SDA Arrears'] + df2['VDA NEx'] + df2['VDA Arrears']) <= (1 + 0.005) * threshold_percentage_da * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    filtered_data_non_executives.insert(1, 'DA Percentage', (filtered_data_non_executives['SDA NEx'] + filtered_data_non_executives['SDA Arrears'] + filtered_data_non_executives['VDA NEx'] + filtered_data_non_executives['VDA Arrears']) / filtered_data_non_executives['Total Basic Pay'] * 100)
    filtered_data_non_executives.insert(0, 'Condition', 'DA')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')

    
def compare_perks():
    global df2

    if df2 is None:
        messagebox.showerror('Error', 'Please load the current payroll dataset first.')
        return

    # Prompt user for the threshold percentage (Hardcoding for demonstration)
    #threshold_percentage_perks = 0.35
        # Check if 'Basic Pay Adjustment' column is present in df2
    if 'Basic Pay Adjustment' in df2.columns:
        basic_pay_adjustment_col = 'Basic Pay Adjustment'
    else:
        # If 'Basic Pay Adjustment' column is not present, fill it with 0
        df2['Basic Pay Adjustment'] = 0
        basic_pay_adjustment_col = 'Basic Pay Adjustment'

    # Compare Perks for Executives
    # Calculate the lower and upper threshold percentages for Executives
    lower_threshold_executives = 0.35 - 0.005
    upper_threshold_executives = 0.35 + 0.005

    # Compare Perks for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    perks_columns_executives = ['Cook Allowance', 'Cook Allow Arr', 'LTC/LTCC Allowance', 'LTC Arr', 'Children Education Allow.',
                                'CEA Arr', 'Hostel Allow.', 'Hostel Allow Arr', 'Professional Dev Allow', 'Prof.DevAllow Arr',
                                'Reim.ProfMembershipFees', 'Reim.ProfMemb Arr', 'Entertainment Allowance', 'Entertainmt Allow Arr',
                                'Kit / Dress Allowance', 'Laundry/Washing Allowance', 'Coal Industry Allow', 'Coal Ind Allow Arr',
                                'Perks (for Old Data)', 'Washing Allowance', 'Washing Allow Arr']
    conditions_executives &= df2[perks_columns_executives].sum(axis=1) < lower_threshold_executives * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    conditions_executives |= df2[perks_columns_executives].sum(axis=1) > upper_threshold_executives * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    filtered_data_executives.insert(1, 'Perks Percentage', df2[perks_columns_executives].sum(axis=1) / (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col]) * 100)
    filtered_data_executives.insert(0, 'Condition', 'Perks')


    # Calculate the lower and upper threshold percentages for Non-Executives
    lower_threshold_non_executives = 0.05 - 0.005
    upper_threshold_non_executives = 0.05 + 0.005

    # Compare Perks for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    perks_columns_non_executives = ['Cook Allowance', 'Cook Allow Arr', 'LTC/LTCC Allowance', 'LTC Arr', 'Children Education Allow.',
                                    'CEA Arr', 'Hostel Allow.', 'Hostel Allow Arr', 'Professional Dev Allow', 'Prof.DevAllow Arr',
                                    'Reim.ProfMembershipFees', 'Reim.ProfMemb Arr', 'Entertainment Allowance', 'Entertainmt Allow Arr',
                                    'Kit / Dress Allowance', 'Laundry/Washing Allowance', 'Coal Industry Allow', 'Coal Ind Allow Arr',
                                    'Perks (for Old Data)', 'Washing Allowance', 'Washing Allow Arr']
    conditions_non_executives &= df2[perks_columns_non_executives].sum(axis=1) < lower_threshold_non_executives * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    conditions_non_executives |= df2[perks_columns_non_executives].sum(axis=1) > upper_threshold_non_executives * (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    filtered_data_non_executives.insert(1, 'Perks Percentage', df2[perks_columns_non_executives].sum(axis=1) / (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col]) * 100)
    filtered_data_non_executives.insert(0, 'Condition', 'Perks')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')


#Function to Compare CMPF for both groups (Executives and Non-Executives)
def compare_cmpf():
    global df2

    if df2 is None:
        messagebox.showerror('Error', 'Please load the current payroll dataset first.')
        return

    # Prompt user for the threshold percentage (Hardcoding for demonstration)
    threshold_percentage_cmps = 0.07
    # Check if 'Basic Pay Adjustment' column is present in df2
    if 'Basic Pay Adjustment' in df2.columns:
        basic_pay_adjustment_col = 'Basic Pay Adjustment'
    else:
        # If 'Basic Pay Adjustment' column is not present, fill it with 0
        df2['Basic Pay Adjustment'] = 0
        basic_pay_adjustment_col = 'Basic Pay Adjustment'

    # Calculate the lower and upper threshold percentages
    lower_threshold_cmps = threshold_percentage_cmps - 0.005
    upper_threshold_cmps = threshold_percentage_cmps + 0.005

    # Calculate CMPS percentage
    df2['CMPF Percentage'] = ((df2['Employee PF'] ) / (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])) * 100

    # Compare CMPS for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    conditions_executives &= ((df2['CMPF Percentage'] < (threshold_percentage_cmps + 0.5)) & (df2['CMPF Percentage'] > (threshold_percentage_cmps - 0.5)))
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    if 'CMPF Percentage' in filtered_data_executives.columns:
        filtered_data_executives.drop('CMPF Percentage', axis=1, inplace=True)
    filtered_data_executives.insert(1, 'CMPF Percentage', df2.loc[conditions_executives, 'CMPF Percentage'])
    filtered_data_executives.insert(0, 'Condition', 'CMPF')

    # Compare CMPS for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    conditions_non_executives &= ((df2['CMPF Percentage'] < (threshold_percentage_cmps + 0.5)) & (df2['CMPF Percentage'] > (threshold_percentage_cmps - 0.5)))
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    if 'CMPF Percentage' in filtered_data_non_executives.columns:
        filtered_data_non_executives.drop('CMPF Percentage', axis=1, inplace=True)
    filtered_data_non_executives.insert(1, 'CMPF Percentage', df2.loc[conditions_non_executives, 'CMPF Percentage'])
    filtered_data_non_executives.insert(0, 'Condition', 'CMPF')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')




# Function to compare CMPS for both groups (Executives and Non-Executives)
def compare_cmps():
    global df2

    if df2 is None:
        messagebox.showerror('Error', 'Please load the current payroll dataset first.')
        return

    # Prompt user for the threshold percentage (Hardcoding for demonstration)
    threshold_percentage_cmps = 0.07
    # Check if 'Basic Pay Adjustment' column is present in df2
    if 'Basic Pay Adjustment' in df2.columns:
        basic_pay_adjustment_col = 'Basic Pay Adjustment'
    else:
        # If 'Basic Pay Adjustment' column is not present, fill it with 0
        df2['Basic Pay Adjustment'] = 0
        basic_pay_adjustment_col = 'Basic Pay Adjustment'

    # Calculate the lower and upper threshold percentages
    lower_threshold_cmps = threshold_percentage_cmps - 0.005
    upper_threshold_cmps = threshold_percentage_cmps + 0.005

    # Calculate CMPS percentage
    df2['CMPS Percentage'] = ((df2['CMPS EE Dedn'] + df2['CMPS EE Dedn Arr']) / (df2['Basic Pay'] + df2['Basic Pay Arrears'] + df2[basic_pay_adjustment_col])) * 100

    # Compare CMPS for Executives
    conditions_executives = (df2['Employee Group'].isin(['Executives', 'Board Level']))
    conditions_executives &= ((df2['CMPS Percentage'] < (threshold_percentage_cmps + 0.5)) & (df2['CMPS Percentage'] > (threshold_percentage_cmps - 0.5)))
    filtered_data_executives = df2.loc[conditions_executives].dropna(how='all')
    if 'CMPS Percentage' in filtered_data_executives.columns:
        filtered_data_executives.drop('CMPS Percentage', axis=1, inplace=True)
    filtered_data_executives.insert(1, 'CMPS Percentage', df2.loc[conditions_executives, 'CMPS Percentage'])
    filtered_data_executives.insert(0, 'Condition', 'CMPS')

    # Compare CMPS for Non-Executives
    conditions_non_executives = (df2['Employee Group'].isin(['Non-Executives', 'MMC (Mon Mtry Comp)']))
    conditions_non_executives &= ((df2['CMPS Percentage'] < (threshold_percentage_cmps + 0.5)) & (df2['CMPS Percentage'] > (threshold_percentage_cmps - 0.5)))
    filtered_data_non_executives = df2.loc[conditions_non_executives].dropna(how='all')
    if 'CMPS Percentage' in filtered_data_non_executives.columns:
        filtered_data_non_executives.drop('CMPS Percentage', axis=1, inplace=True)
    filtered_data_non_executives.insert(1, 'CMPS Percentage', df2.loc[conditions_non_executives, 'CMPS Percentage'])
    filtered_data_non_executives.insert(0, 'Condition', 'CMPS')

    # Save the compared data to Excel
    save_to_excel(filtered_data_executives, 'Executives')
    save_to_excel(filtered_data_non_executives, 'Non-Executives')

    
    
def compare_employee_ids():
    global df1, df2

    if df1 is None or df2 is None:
        messagebox.showerror('Error', 'Please load both datasets first.')
        return

    # Get unique employee IDs from both datasets
    unique_employee_ids_df1 = set(df1['Person No'])
    unique_employee_ids_df2 = set(df2['Person No'])

    # Find missing employees (in df1 but not in df2) and new employees (in df2 but not in df1)
    missing_employees = unique_employee_ids_df1 - unique_employee_ids_df2
    new_employees = unique_employee_ids_df2 - unique_employee_ids_df1

    # Create DataFrames to store the results
    missing_employees_df = pd.DataFrame({'Missing Employees': list(missing_employees)})
    new_employees_df = pd.DataFrame({'New Employees': list(new_employees)})

    # Save the results to an Excel file
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=(('Excel Files', '*.xlsx'), ('All Files', '*.*')))
    if file_path:
        try:
            with pd.ExcelWriter(file_path) as writer:
                missing_employees_df.to_excel(writer, sheet_name='Missing Employees', index=False)
                new_employees_df.to_excel(writer, sheet_name='New Employees', index=False)
            messagebox.showinfo('Success', 'Comparison results saved as Excel successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save comparison results:\n{str(e)}')

# Function to save the filtered data to Excel
def save_to_excel(filtered_data, employee_group):
    if filtered_data is None or filtered_data.empty:
        messagebox.showwarning('No Data', f'No {employee_group} result to save.')
        return

    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=(('Excel Files', '*.xlsx'), ('All Files', '*.*')))
    if file_path:
        try:
            with pd.ExcelWriter(file_path) as writer:
                filtered_data.to_excel(writer, index=False)
            messagebox.showinfo('Success', f'{employee_group} result saved as Excel successfully.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save {employee_group} result:\n{str(e)}')


text_widget = None
def toggle_theme():
    global text_widget, current_theme_index
    
    # Define different color schemes for themes
    themes = [
        {
            'name': 'Default',
            'bg_color': 'white',
            'fg_color': 'black',
            'accent_color': '#0078D4'  # A blue accent color
        },
        {
            'name': 'Dark Mode',
            'bg_color': 'black',
            'fg_color': 'white',
            'accent_color': '#FF5733'  # An orange accent color
        },
        {
            'name': 'Green Dream',
            'bg_color': '#1C1C1C',  # A dark gray background
            'fg_color': '#F0F0F0',  # Light gray foreground
            'accent_color': '#33FF57'  # A green accent color
        },
        {
            'name': 'Soft Pink',
            'bg_color': '#F8E9E9',  # A light pink background
            'fg_color': '#4A4A4A',  # A dark gray foreground
            'accent_color': '#E84393'  # A pink accent color
        },
        {
            'name': 'Sunny Day',
            'bg_color': '#FFF3B0',  # A pale yellow background
            'fg_color': '#474747',  # A dark gray foreground
            'accent_color': '#FFC107'  # A yellow accent color
        },
        {
            'name': 'Purple Haze',
            'bg_color': '#1E1B26',  # A dark purple background
            'fg_color': '#EDEDED',  # Light gray foreground
            'accent_color': '#9B59B6'  # A purple accent color
        },
        {
            'name': 'Ocean Blue',
            'bg_color': '#F0F7FF',  # A pale blue background
            'fg_color': '#333333',  # A dark gray foreground
            'accent_color': '#3498DB'  # A blue accent color
        },
        {
            'name': 'Sunset Red',
            'bg_color': '#F5D1D0',  # A light red background
            'fg_color': '#5A5A5A',  # A dark gray foreground
            'accent_color': '#E74C3C'  # A red accent color
        },
        {
            'name': 'Minty Fresh',
            'bg_color': '#E0FFF3',  # A mint green background
            'fg_color': '#545454',  # A dark gray foreground
            'accent_color': '#00B894'  # A green accent color
        }
        # Add more themes here as dictionaries
    ]

    # Cycle to the next theme
    current_theme_index = (current_theme_index + 1) % len(themes)

    # Get the current theme
    current_theme_values = themes[current_theme_index]

    # Update the window background color
    window.config(bg=current_theme_values['bg_color'])

    # Update the colors and fonts of the widgets
    for widget in widgets_to_style:
        widget.config(bg=current_theme_values['bg_color'], fg=current_theme_values['fg_color'])

    # Update the font and color of the text widget
    text_widget.config(font=('Arial', 10), fg=current_theme_values['fg_color'], bg=current_theme_values['bg_color'])

    # Update fonts for specific widgets
    label_dataset1.config(font=('Arial', 10, 'bold'))
    label_dataset2.config(font=('Arial', 10, 'bold'))
    footnote.config(font=('Arial', 8))
    toggle_button.config(
        bg=current_theme_values['accent_color'],
        fg='white',
        activebackground=current_theme_values['accent_color'],
        activeforeground='white'
    )

    # Update theme for ttk widgets
    style = ttk.Style()
    style.configure('TLabel', background=current_theme_values['bg_color'], foreground=current_theme_values['fg_color'], font=('Arial', 10))
    style.configure('TButton', background=current_theme_values['accent_color'], foreground='white', font=('Arial', 10), padx=10, pady=5)
    style.map('TButton', background=[('active', '!disabled', 'black')])
    style.configure('TEntry', fieldbackground=current_theme_values['bg_color'], font=('Arial', 10))
    style.map('TEntry', fieldbackground=[('focus', current_theme_values['accent_color'])])
    style.configure('TCombobox', font=('Arial', 10))
    style.configure('Treeview', fieldbackground=current_theme_values['bg_color'], foreground=current_theme_values['fg_color'], font=('Arial', 10))

    # Update fonts and colors of all text widgets in the window
    all_text_widgets = [widget for widget in window.winfo_children() if isinstance(widget, (tk.Text, tk.Label))]
    for text_widget in all_text_widgets:
        text_widget.config(font=('Arial', 10), fg=current_theme_values['fg_color'])

# Initialize the current_theme_index
current_theme_index = 0



# Create the widgets using the grid layout
label_dataset1 = tk.Label(window, text='Dataset 1:')
button_load_dataset1 = tk.Button(window, text='Load Previous Payroll', command=load_dataset1)

label_dataset2 = tk.Label(window, text='Dataset 2:')
button_load_dataset2 = tk.Button(window, text='Load Current Payroll', command=load_dataset2)

label_threshold_hra = tk.Label(window, text='HRA (%):')
entry_threshold_hra = tk.Entry(window)

label_threshold_da = tk.Label(window, text='DA (%):')
entry_threshold_da = tk.Entry(window)

button_compare_basic_pay = tk.Button(window, text='Compare Basic Pay', command=compare_basic_pay)
button_compare_hra = tk.Button(window, text='Compare HRA', command=compare_hra)
button_compare_da = tk.Button(window, text='Compare DA', command=compare_da)
button_compare_perks = tk.Button(window, text='Compare Perks', command=compare_perks)
button_compare_cmpf = tk.Button(window, text='Compare CMPF', command=compare_cmpf)
button_compare_cmps = tk.Button(window, text='Compare CMPS', command=compare_cmps)
button_compare_employee_ids = tk.Button(window, text='Compare Employee IDs', command=compare_employee_ids)

# Create the text widget
text_widget = tk.Text(window, height=3, width=30)
text_widget.insert(tk.END, "Payroll Comparison Tool\nDeveloped by I-Cell, CMPDI")
text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

# Set the tag for center alignment
text_widget.tag_configure("center", justify='center')

# Apply the tag to the whole text
text_widget.tag_add("center", "1.0", "end")

text_widget.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky='ew')


# Place the widgets in the grid layout
label_dataset1.grid(row=1, column=0, sticky='w', padx=20, pady=10)
button_load_dataset1.grid(row=1, column=1, padx=20, pady=10, sticky='ew')

label_dataset2.grid(row=2, column=0, sticky='w', padx=20, pady=10)
button_load_dataset2.grid(row=2, column=1, padx=20, pady=10, sticky='ew')

label_threshold_hra.grid(row=3, column=0, sticky='w', padx=20, pady=10)
entry_threshold_hra.grid(row=3, column=1, padx=20, pady=10, sticky='ew')

label_threshold_da.grid(row=4, column=0, sticky='w', padx=20, pady=10)
entry_threshold_da.grid(row=4, column=1, padx=20, pady=10, sticky='ew')

button_compare_basic_pay.grid(row=5, column=1, padx=20, pady=10, sticky='ew')
button_compare_hra.grid(row=6, column=1, padx=20, pady=10, sticky='ew')
button_compare_da.grid(row=7, column=1, padx=20, pady=10, sticky='ew')
button_compare_perks.grid(row=8, column=1, padx=20, pady=10, sticky='ew')
button_compare_cmpf.grid(row=9, column=1, padx=20, pady=10, sticky='ew')
button_compare_cmps.grid(row=10, column=1, padx=20, pady=10, sticky='ew')
button_compare_employee_ids.grid(row=11, column=1, padx=20, pady=10, sticky='ew')

# Add a footer frame
footer_frame = tk.Frame(window)
footer_frame.grid(row=12, column=0, columnspan=1, padx=1, pady=5, sticky='sw')

# Add a footnote aligned to the left side
footnote = tk.Label(footer_frame, text='Version 2\nDeveloper\nAryaman\nJuly 2023', font=('Arial', 8), anchor='w')
footnote.pack()

# Add a button to toggle light/dark mode
current_theme = tk.StringVar()
current_theme.set('dark')  # Set the default theme to light
toggle_button = tk.Button(window, text='Toggle Theme', command=toggle_theme)
toggle_button.grid(row=12, column=1, padx=10, pady=15, sticky='se')


# Create the list of widgets to style
widgets_to_style = [
    label_dataset1, button_load_dataset1, label_dataset2, button_load_dataset2,
    label_threshold_hra, entry_threshold_hra, label_threshold_da, entry_threshold_da,
    button_compare_basic_pay, button_compare_hra, button_compare_da,
    button_compare_perks, button_compare_cmpf, button_compare_cmps, footnote, toggle_button, button_compare_employee_ids
]


# Apply grid layout settings to ensure proper spacing
window.grid_rowconfigure(12, weight=1)
window.grid_columnconfigure(1, weight=1)

# Start the main loop
window.mainloop()


