#Importiere die benötigten Pakete
from dash import html #hiermit wird automatisch eine HTML-Struktur generiert
from dash import dcc #dcc: Dash Core Components für Markdown, beinhaltet z.B. Syntax für Textdarstellung
from dash import dash_table #interaktive Tabellenkomponente für Daten
import dash #dash ist ein web app framework für Python
from dash import Dash
from dash.dependencies import Input, Output, State
import pandas as pd

import datetime

import base64 #zur Datendekodierung von byte-Objekten oder ASCII-Strings
import io #um files lesen zu können


#erstelle die App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True

#erstelle Das Layout der App
app.layout = html.Div([

#erstelle Feld, für Drag- and Drop, um Daten hochzuladen
                html.H5("Upload Files"),
                dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files') #Hyperlink
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=True,

                ),



                html.Br(),
                html.H5("Updated Table"),
                html.Div(id='output-data-upload'),
                ])

# Funktionen
# Funktion um Datei hochzladen
def parse_contents(contents, filename, date):
    #contents ist später unsere list_of_contents ['data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,UEsDBBQACAgIAMp....
    #
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    #so sieht dekodierter content-string in bytes aus: b'PK\x03\x04\x14\x00\x08\x08\x08\x00\xcaNXU\x00\x00\x00\x00\
    try:
        if 'csv' in filename:
            # Angenommen, eine csv-Datei wurde hochgeladen
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),sep=";")
            df.to_sql('table1', "sqlite:///database11.db", if_exists='replace', index=False)
        elif 'xlsx' in filename:
            # Angenommen, eine Excel-Datei wurde hochgeladen
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_sql('table1', "sqlite:///database11.db", if_exists ='replace', index = False )
        else:
            raise ValueError("Falscher Dateityp-nur XLSX oder CSV erlaubt!")
    except ValueError as ve:
        print(ve)
        return html.Div([
            'Falsches Dateiformat-nur XLSX oder CSV erlaubt'
        ])
    except Exception as e:
        print("Fehler: ",e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),


        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns], editable=True, export_format='xlsx',
                        export_headers='display',
                        merge_duplicate_headers=True
        ),
        html.Hr(),  # horizontale Linie

    ])

# callback Tabellenerstellung
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)