# Payroll Comparison Tool Project

The Payroll Comparison Tool is a Python-based desktop application that allows users to compare payroll data from two datasets. It aims to assist in identifying differences in various payroll components between two payrolls, helping HR personnel and payroll administrators to ensure accuracy and detect discrepancies.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [How it Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Payroll Comparison Tool is a GUI-based application developed in Python using the Tkinter library. It enables users to load two datasets in different file formats (CSV or Excel) representing two payrolls and compare specific payroll components such as Basic Pay, House Rent Allowance (HRA), Dearness Allowance (DA), Perks, Contributory Provident Fund (CMPF), Contributory Medical Protection Scheme (CMPS), and Employee IDs.

## Features

- Load two payroll datasets in CSV or Excel format.
- Compare Basic Pay for Executives and Non-Executives.
- Compare House Rent Allowance (HRA) for Executives and Non-Executives.
- Compare Dearness Allowance (DA) for Executives and Non-Executives.
- Compare Perks for Executives and Non-Executives.
- Compare Contributory Provident Fund (CMPF) for Executives and Non-Executives.
- Compare Contributory Medical Protection Scheme (CMPS) for Executives and Non-Executives.
- Compare Employee IDs to find missing and new employees between datasets.

## Installation

1. Clone this repository to your local machine:

   ```
   git clone https://github.com/your_username/payroll-comparison-tool.git
   ```

2. Navigate to the project directory:

   ```
   cd payroll-comparison-tool
   ```

3. Install the required dependencies (see [Dependencies](#dependencies) section).

## Usage

1. Run the application:

   ```
   python payroll_comparison_tool.py
   ```

2. Load the previous payroll dataset using the "Load Previous Payroll" button.
3. Load the current payroll dataset using the "Load Current Payroll" button.
4. Select the comparison type from the available options (e.g., Basic Pay, HRA, DA, Perks, CMPF, CMPS, Employee IDs).
5. Configure any specific thresholds (e.g., for HRA or DA comparison) if applicable.
6. Click the corresponding "Compare" button to perform the comparison.
7. The results will be displayed in a new window, and you can save the comparison data as an Excel file.

## Dependencies

The Payroll Comparison Tool relies on the following dependencies:

- Python 3.x
- NumPy
- pandas
- tkinter (included with Python)
- Pillow (PIL)
- openpyxl (for Excel support)
- ttk (themed widgets from tkinter)

Install the dependencies using the following command:

```
pip install numpy pandas Pillow openpyxl
```

## How it Works

1. The application uses Python's Tkinter library to create a graphical user interface (GUI) for the tool.
2. Users can load two payroll datasets in CSV or Excel format using the "Load Previous Payroll" and "Load Current Payroll" buttons.
3. After loading the datasets, users can select the type of comparison they want to perform (e.g., Basic Pay, HRA, DA, etc.).
4. The tool then calculates the comparison results based on the selected type and displays the data in a new window.
5. Users have the option to save the comparison results as an Excel file.

## Contributing

Contributions to the Payroll Comparison Tool project are welcome! If you find any issues or have suggestions for new features, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
