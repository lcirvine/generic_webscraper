import argparse
import os
from webscraper import WebScraper
from logging_webscraper import logger

arg_parser = argparse.ArgumentParser(description='Generic tool to scrape table data from websites.')
arg_parser.add_argument('-browser', help='Browser that will be used', choices=(None, 'Firefox', 'Chrome'), default=None)
arg_parser.add_argument('-url', type=str, help='Website to scrape', required=True)
arg_parser.add_argument('-table_elem', type=str, help='The element to search for on the website', default='table')
arg_parser.add_argument('-table_attrs_key', type=str, help='The key of the table attribute', required=False)
arg_parser.add_argument('-table_attrs_val', type=str, help='The value of the table attribute', required=False)
arg_parser.add_argument('-table_num', type=str, help='If there are multiple table elements, which one should be returned?', required=False)
arg_parser.add_argument('-row_elem', type=str, help='The row element of the table', default='tr')
arg_parser.add_argument('-cell_elem', type=str, help='The cell element of the table', default='td')
arg_parser.add_argument('-header_elem', type=str, help='The header (columns) element of the table', default='th', required=False)
arg_parser.add_argument('-include_links', default=False, required=False)
arg_parser.add_argument('-folder', type=str, help='The folder where the results will be saved', required=True)
arg_parser.add_argument('-file_name', type=str, help='The name the results will be saved as', required=True)
arg_parser.add_argument('-file_type', type=str, help='The type of file (.csv, .xlsx)', choices=('.csv', '.xlsx'), default='.csv')
args = arg_parser.parse_args()

all_args = vars(args)

browser_selected = all_args.pop('browser')
url = all_args.pop('url')
link_opt = all_args.pop('include_links')
if link_opt:
    incl_links = True
else:
    incl_links = False

folder = all_args.pop('folder')
file_name = all_args.pop('file_name')
file_type = all_args.pop('file_type')

ws = WebScraper(browser=browser_selected)
ws.parse_table(url, incl_links, **all_args)
df = ws.return_df()
if df is not None and len(df) > 0:
    if file_type == '.csv':
        df.to_csv(os.path.join(folder, f"{file_name}{file_type}"), index=False, encoding='utf-8-sig')
    elif file_type == '.xlsx':
        df.to_excel(os.path.join(folder, f"{file_name}{file_type}"), index=False, encoding='utf-8-sig')
