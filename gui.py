import os
import sys
import random
import PySimpleGUI as sg
from webscraper import WebScraper
from logging_webscraper import logger


def main():
    with open('themes.txt', 'r') as f:
        fave_themes = list(set(f.read().split('\n')))
    window_theme = random.choice(fave_themes)

    sg.theme(window_theme)

    col_web_1 = [
        [sg.Text('URL')],
        [sg.Text('Table Element')],
        [sg.Text('Table Number')],
        [sg.Text('Table Attributes')],
        [sg.Text('Row Element')],
        [sg.Text('Cell Element')],
        [sg.Text('Header Element')],
        [sg.Text('Links')]
    ]
    std_size = (35, 1)
    col_web_2 = [
        [sg.InputText(key='url', size=std_size)],
        [sg.InputText('table', key='table_elem', size=std_size)],
        [sg.InputText(key='table_num', size=std_size)],
        [sg.InputText(key='table_attrs_key', size=(16, 1)), sg.InputText(key='table_attrs_val', size=(17, 1))],
        [sg.InputText('tr', key='row_elem', size=std_size)],
        [sg.InputText('td', key='cell_elem', size=std_size)],
        [sg.InputText('th', key='header_elem', size=std_size)],
        [sg.Checkbox(text='', key='include_links', size=std_size)]
    ]
    col_save_1 = [
        [sg.Text('Folder')],
        [sg.Text('File Name')]
    ]

    col_save_2 = [
        [sg.InputText(key='folder', size=(40, 1)), sg.FolderBrowse()],
        [sg.InputText(key='file', size=(39, 1)), sg.InputCombo(values=['.csv', '.xlsx'], default_value='.csv', key='file_type')]
    ]

    layout = [[
        [sg.Frame('Browser', [
            [sg.InputCombo(values=[None, 'Firefox', 'Chrome'], default_value=None, key='browser'),
             sg.Checkbox(text='Headless?', key='headless', default=True),
             sg.Button('Create Browser', focus=True, button_color=('white', 'blue'), key='create_browser')]
        ], border_width=3)],
        [sg.Frame('Website', [
            [sg.Column(col_web_1, element_justification='l'),
            sg.Column(col_web_2, element_justification='l')]
        ], border_width=3)],
    [sg.Button('Scrape Website', disabled=True, button_color=('white', 'blue'), key='scrape'),
     sg.Button('Clear Data', disabled=True, button_color=('black', 'yellow'), key='clear')],
    [sg.Column(col_save_1, element_justification='r'), sg.Column(col_save_2, element_justification='l')],
    [sg.Button('Exit', button_color=('white', 'red')), sg.Button('Save', bind_return_key=True, disabled=True, button_color=('white', 'green'))],
    [sg.Multiline('Click Create Browser to begin', size=(60, 5), key='ws_status')]
    ]]

    window = sg.Window('Generic Webscraper', layout)
    ws = None
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            if ws is not None:
                ws.close()
            break
        if event == 'create_browser':
            browser_selected = values['browser']
            ws = WebScraper(browser=browser_selected, headless=values['headless'])
            window['scrape'].update(disabled=False)
            window['ws_status'].update('Provide website data, then click Scrape Website')
        if event == 'scrape':
            url = values['url']
            if url == '' or url is None:
                window['ws_status'].update('Please enter a URL')
            else:
                try:
                    logger.info(f"URL - {url}")
                    ws_data = {
                        'table_elem': values['table_elem'],
                        'table_attrs': {values['table_attrs_key']: values['table_attrs_val']},
                        'table_num': values['table_num'],
                        'row_elem': values['row_elem'],
                        'cell_elem': [x.strip() for x in values['cell_elem'].split(',')],
                        'header_elem': values['header_elem']
                    }
                    for null_value in [k for k, v in ws_data.items() if v == '' or v == {'': ''}]:
                        ws_data.pop(null_value)
                    ws.parse_table(url, values['include_links'], **ws_data)
                    df = ws.return_df()
                    if df is not None and len(df) > 0:
                        window['ws_status'].update(f"{len(df)} rows found in table\n\n{df.head(5).to_string(na_rep='')}")
                        window['Save'].update(disabled=False)
                        window['clear'].update(disabled=False)
                    else:
                        status_text = f"Unable to find data using inputs provided\n" \
                                      f"\n{ws.return_element_attrs(values['table_elem'])}"
                        window['ws_status'].update(status_text)
                        logger.info(status_text)
                except Exception as e:
                    logger.error(e, exc_info=sys.exc_info())
                    window['ws_status'].update(f"Error\n{e}")
                    if ws is not None:
                        ws.close()
        if event == 'clear':
            ws.clear_dataframe()
            window['ws_status'].update('Provide website data, then click Scrape Website')
            window['clear'].update(disabled=True)
            window['Save'].update(disabled=True)
        if event == 'Save':
            folder = values['folder']
            file = values['file']
            file_type = values['file_type']
            if folder is None or folder == '':
                window['ws_status'].update('Please enter a folder')
            elif file is None or file == '':
                window['ws_status'].update('Please enter a file name')
            else:
                if file_type == '.csv':
                    df.to_csv(os.path.join(folder, f"{file}{file_type}"), index=False, encoding='utf-8-sig')
                elif file_type == '.xlsx':
                    df.to_excel(os.path.join(folder, f"{file}{file_type}"), index=False, encoding='utf-8-sig')
                window['ws_status'].update('Data saved')


if __name__ == '__main__':
    main()
