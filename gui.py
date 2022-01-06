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
    print(window_theme)

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
    col_web_2 = [
        [sg.InputText(key='url')],
        [sg.InputText('table', key='table_elem')],
        [sg.InputText(key='table_num')],
        [sg.InputText(key='table_attrs')],
        [sg.InputText('tr', key='row_elem')],
        [sg.InputText('td', key='cell_elem')],
        [sg.InputText('th', key='header_elem')],
        [sg.Checkbox(text='', key='include_links')]
    ]
    col_save_1 = [
        [sg.Text('Folder')],
        [sg.Text('File Name')]
    ]
    col_save_2 = [
        [sg.InputText(key='folder'), sg.FolderBrowse()],
        [sg.InputText(key='file'), sg.InputCombo(values=['.csv', '.xlsx'], default_value='.csv', key='file_type')]
    ]

    layout = [[
        [sg.Frame('Browser', [
            [sg.InputCombo(values=['Firefox', 'Chrome'], default_value='Firefox', key='browser'),
             sg.Checkbox(text='Headless?', key='headless', default=True),
             sg.Button('Create Browser', focus=True, button_color=('white', 'blue'), key='create_browser')]
        ], border_width=3)],
        [sg.Frame('Website', [
            [sg.Column(col_web_1, element_justification='l'),
            sg.Column(col_web_2, element_justification='l')]
        ], border_width=3)],
    [sg.Button('Scrape Website', disabled=True, button_color=('white', 'blue'), key='scrape')],
    [sg.Column(col_save_1, element_justification='r'), sg.Column(col_save_2, element_justification='l')],
    [sg.Button('Exit', button_color=('white', 'red')), sg.Button('Save', disabled=True, button_color=('white', 'green'))],
    [sg.Text('Info:'), sg.Text('Click Create Browser to begin', size=(50, 1), key='ws_status')]
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
            ws = WebScraper(browser=values['browser'], headless=values['headless'])
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
                        'table_attrs': values['table_attrs'],
                        'table_num': values['table_num'],
                        'row_elem': values['row_elem'],
                        'cell_elem': values['cell_elem'],
                        'header_elem': values['header_elem']
                    }
                    for null_value in [k for k, v in ws_data.items() if v == '']:
                        ws_data.pop(null_value)
                    for k, v in ws_data.items():
                        logger.info(f"{k} = {v}")
                    ws.parse_table(url, values['include_links'], **ws_data)
                    df = ws.return_df()
                    if df is not None and len(df) > 0:
                        window['ws_status'].update(f"{len(df)} rows found in table")
                        window['Save'].update(disabled=False)
                except Exception as e:
                    logger.error(e, exc_info=sys.exc_info())
                    window['ws_status'].update(f"Error - see logs")
                    if ws is not None:
                        ws.close()
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
