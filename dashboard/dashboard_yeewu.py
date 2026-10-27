import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

# ==============================================================================
# 1. SIMULATION & CHARGEMENT DES DONNÉES
# ==============================================================================
np.random.seed(42)
n_samples = 500
regions = ['Dakar', 'Thiès', 'Saint-Louis', 'Kaolack', 'Mbour', 'Ziguinchor']

df = pd.DataFrame({
    'parcelle_id': [f'PARC-{i:03d}' for i in range(1, n_samples + 1)],
    'region': np.random.choice(regions, size=n_samples, p=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10]),
    'superficie_m2': np.random.randint(150, 2000, size=n_samples),
    'score_risque': np.round(np.random.beta(a=2, b=2, size=n_samples), 2),
    'litige_confirme': np.random.choice([0, 1], size=n_samples, p=[0.58, 0.42])
})

# ==============================================================================
# 2. INITIALISATION DE L'APPLICATION DASH
# ==============================================================================
# Utilisation du thème Flatly de Bootstrap pour un rendu professionnel
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Yeewu-SN | Intelligence Foncière"

# ==============================================================================
# 3. INTERFACE GRAPHIQUE (LAYOUT)
# ==============================================================================
app.layout = dbc.Container([
    # En-tête
    dbc.Row([
        dbc.Col([
            html.H1("Idu Yeewu-SN", className="text-primary fw-bold mt-3 mb-1"),
            html.P("Plateforme d'Intelligence Foncière — Cartographie et Prévention des Risques en Temps Réel", className="text-muted fs-5"),
            html.Hr()
        ])
    ]),

    # Filtres interactifs
    dbc.Row([
        dbc.Col([
            html.Label("Filtrer par Région :", className="fw-bold mb-1"),
            dcc.Dropdown(
                id='filter-region',
                options=[{'label': r, 'value': r} for r in sorted(df['region'].unique())],
                multi=True,
                placeholder="Toutes les régions"
            )
        ], md=6),
        dbc.Col([
            html.Label("Seuil Minimal du Score de Risque :", className="fw-bold mb-1"),
            dcc.Slider(
                id='filter-risk-slider',
                min=0.0, max=1.0, step=0.05, value=0.0,
                marks={0: '0.0', 0.5: '0.5', 1.0: '1.0'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=6)
    ], className="bg-light p-3 rounded mb-4 shadow-sm"),

    # Cartes KPI (Indicateurs clés)
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Total Parcelles", className="text-muted"), html.H2(id="kpi-total", className="text-primary fw-bold")])], className="shadow-sm border-start border-primary border-4"), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Cas Litigieux Détectés", className="text-muted"), html.H2(id="kpi-litiges", className="text-danger fw-bold")])], className="shadow-sm border-start border-danger border-4"), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Taux de Litiges", className="text-muted"), html.H2(id="kpi-taux", className="text-warning fw-bold")])], className="shadow-sm border-start border-warning border-4"), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Score de Risque Moyen", className="text-muted"), html.H2(id="kpi-score-moyen", className="text-info fw-bold")])], className="shadow-sm border-start border-info border-4"), md=3),
    ], className="mb-4"),

    # Graphiques
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph-region'), md=6),
        dbc.Col(dcc.Graph(id='graph-risk-dist'), md=6)
    ], className="mb-4"),

    # Tableau de données détaillé
    dbc.Row([
        dbc.Col([
            html.H4("Détail des Parcelles à Risque", className="fw-bold mb-3"),
            dash_table.DataTable(
                id='datatable-parcelles',
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                # Coloration conditionnelle : si le risque est > 0.70, la ligne devient rouge
                style_data_conditional=[{
                    'if': {'filter_query': '{score_risque} >= 0.70'},
                    'backgroundColor': '#f8d7da',
                    'color': '#721c24',
                    'fontWeight': 'bold'
                }]
            )
        ])
    ], className="mb-5")
], fluid=True)

# ==============================================================================
# 4. LOGIQUE INTERACTIVE (CALLBACKS)
# ==============================================================================
@app.callback(
    [Output('kpi-total', 'children'),
     Output('kpi-litiges', 'children'),
     Output('kpi-taux', 'children'),
     Output('kpi-score-moyen', 'children'),
     Output('graph-region', 'figure'),
     Output('graph-risk-dist', 'figure'),
     Output('datatable-parcelles', 'data')],
    [Input('filter-region', 'value'),
     Input('filter-risk-slider', 'value')]
)
def update_dashboard(selected_regions, min_risk):
    # 1. Filtrage des données selon les critères de l'utilisateur
    filtered_df = df[df['score_risque'] >= min_risk]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
        
    # 2. Calcul des indicateurs
    total = len(filtered_df)
    litiges = filtered_df['litige_confirme'].sum()
    taux = f"{(litiges / total * 100):.1f}%" if total > 0 else "0%"
    score_moyen = f"{filtered_df['score_risque'].mean():.2f}" if total > 0 else "0.00"
    
    # 3. Mise à jour du graphique par région
    fig_region = px.histogram(
        filtered_df, x='region', color='litige_confirme',
        title="<b>Nombre de Parcelles et Litiges par Région</b>",
        labels={'region': 'Région', 'count': 'Nombre de Parcelles', 'litige_confirme': 'Litige'},
        color_discrete_map={0: '#2ecc71', 1: '#e74c3c'},
        barmode='group'
    )
    fig_region.update_layout(template='plotly_white')

    # 4. Mise à jour de la distribution des risques
    fig_risk = px.histogram(
        filtered_df, x='score_risque', nbins=20,
        title="<b>Distribution du Score de Risque Foncier</b>",
        labels={'score_risque': 'Score de Risque (0 à 1)'},
        color_discrete_sequence=['#3498db']
    )
    # Ajout d'une ligne verticale pour marquer la zone critique
    fig_risk.add_vline(x=0.70, line_dash="dash", line_color="red", annotation_text="Zone Critique (>= 0.70)")
    fig_risk.update_layout(template='plotly_white')
    
    return f"{total}", f"{litiges}", taux, score_moyen, fig_region, fig_risk, filtered_df.to_dict('records')

# ==============================================================================
# 5. EXECUTION DE L'APPLICATION
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True, port=8050)