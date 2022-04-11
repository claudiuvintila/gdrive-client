from __future__ import print_function

import start


class Sheets:
    def __init__(self, service, id):
        self.service = service
        self.id = id

    def get_sheets_list(self):
        spreadsheet_ = self.service.spreadsheets().get(spreadsheetId=self.id).execute()

        sheets_list = [sheet['properties']['title'] for sheet in spreadsheet_['sheets']]

        return sheets_list

    def get_sheet_by_title(self, title='template'):
        spreadsheet_ = self.service.spreadsheets().get(spreadsheetId=self.id).execute()

        for sheet in spreadsheet_['sheets']:
            if sheet['properties']['title'] == title:
                return sheet

    def duplicate(self, source_sheet_name='template', destination_index=0, destination_title='New Sheet'):
        template_sheet_ = self.get_sheet_by_title(source_sheet_name)

        self.service.spreadsheets().create(fields='spreadsheetId', body={
            'properties': {
                'title': destination_title
            }
        }).execute()
        # print('Spreadsheet ID: {0}'.format(body.get('spreadsheetId')))

        sheet_id_ = template_sheet_['properties']['sheetId']
        copied_sheet = self.service.spreadsheets().sheets().copyTo(
            spreadsheetId=self.id,
            sheetId=sheet_id_,
            body={
                # The ID of the spreadsheet to copy the sheet to.
                'destination_spreadsheet_id': self.id
            }
        ).execute()

        body = {
            'requests': {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": copied_sheet['sheetId'],
                        "title": destination_title,
                        "index": destination_index
                    },
                    "fields": "title,index",
                }
            }
        }

        self.service.spreadsheets().batchUpdate(spreadsheetId=self.id, body=body).execute()

    def append(self, sheet_range, data=[[]]):
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.id,
            range=sheet_range,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': data}
        ).execute()

    def get_sheet_values(self, ranges_):
        return self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.id,
            ranges=ranges_
        ).execute()


if __name__ == '__main__':
    service = start.start()
    spreadsheet = Sheets(service, 'sheet-id')
    print(spreadsheet.get_sheet_values('template!A:Z'))
